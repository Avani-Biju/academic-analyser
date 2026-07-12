from __future__ import annotations

import json
import logging
import os
import time
from urllib import error, parse, request

from app.config import load_environment
from app.llm.schemas import GeminiConfig, GeminiGenerateContentResponse

logger = logging.getLogger(__name__)


class LLMProviderError(RuntimeError):
    def __init__(self, status_code: int, body: str, endpoint: str):
        self.status_code = status_code
        self.body = body
        self.endpoint = endpoint
        self.transient = status_code in {429, 500, 502, 503, 504}
        super().__init__(f"Gemini HTTP error {status_code}: {body}")


class GeminiClient:
    def __init__(self, config: GeminiConfig | None = None):
        load_environment()
        self.config = config or GeminiConfig(
            api_key=os.getenv("GEMINI_API_KEY"),
            model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
            timeout_seconds=float(os.getenv("GEMINI_TIMEOUT_SECONDS", "30")),
        )
        self.base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        self._models_cache: list[dict] | None = None

    def is_available(self) -> bool:
        return bool(self.config.api_key)

    def generate_json(self, prompt: str) -> dict:
        result = self.generate_text(prompt, response_mime_type="application/json")
        try:
            return json.loads(result["response_text"])
        except json.JSONDecodeError as exc:
            logger.error("Gemini returned non-JSON content: %s", result["response_text"][:500])
            raise RuntimeError("Gemini returned invalid JSON") from exc

    def generate_text(self, prompt: str, response_mime_type: str = "text/plain") -> dict:
        if not self.config.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        model_name = self.resolve_model(self.config.model)
        excluded_models: set[str] = set()
        last_error: Exception | None = None

        for attempt in range(1, 4):
            endpoint = self._build_generate_endpoint(model_name)
            logger.info("[LLM] Model: %s", model_name)
            logger.info("[LLM] Endpoint: %s", endpoint.split("?key=")[0])
            logger.info("[LLM] Attempt %s", attempt)
            logger.info("[LLM] Sending request to Gemini")

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "responseMimeType": response_mime_type,
                },
            }

            try:
                status_code, raw = self._request(endpoint, method="POST", payload=payload)
                logger.info("[LLM] Response received")
                parsed = GeminiGenerateContentResponse.model_validate_json(raw)
                text = self._extract_text(parsed)
                if not text:
                    raise RuntimeError("Gemini returned no text content")

                logger.info("[LLM] Success")
                return {
                    "model": model_name,
                    "endpoint": endpoint.split("?key=")[0],
                    "status_code": status_code,
                    "response_text": text,
                    "raw_response": raw,
                }
            except LLMProviderError as exc:
                last_error = exc
                logger.error("[LLM] Provider error status=%s body=%s", exc.status_code, exc.body)

                if exc.status_code == 404:
                    excluded_models.add(self._normalize_model_name(model_name))
                    alternate_model = self.resolve_model(self.config.model, exclude=excluded_models)
                    if alternate_model and self._normalize_model_name(alternate_model) != self._normalize_model_name(model_name):
                        logger.info("[LLM] Switching to supported model: %s", alternate_model)
                        model_name = alternate_model
                        continue

                if exc.transient and attempt < 3:
                    time.sleep(2 ** (attempt - 1))
                    continue

                raise
            except error.URLError as exc:
                last_error = exc
                logger.error("[LLM] Provider connection error: %s", exc.reason)
                if attempt < 3:
                    time.sleep(2 ** (attempt - 1))
                    continue
                raise RuntimeError(f"Gemini connection error: {exc.reason}") from exc

        if last_error:
            raise last_error
        raise RuntimeError("Gemini request failed without a captured error")

    def list_models(self) -> list[dict]:
        if self._models_cache is not None:
            return self._models_cache

        endpoint = f"{self.base_url}/models?key={parse.quote(self.config.api_key or '')}"
        status_code, raw = self._request(endpoint, method="GET")
        payload = json.loads(raw)
        self._models_cache = payload.get("models", [])
        logger.info("[LLM] Available models fetched: %s (HTTP %s)", len(self._models_cache), status_code)
        return self._models_cache

    def resolve_model(self, desired_model: str, exclude: set[str] | None = None) -> str:
        exclude = exclude or set()
        normalized_desired = self._normalize_model_name(desired_model)
        supported_models = [
            model for model in self.list_models()
            if "generateContent" in (model.get("supportedGenerationMethods") or [])
        ]
        supported_names = {
            self._normalize_model_name(model.get("name", "")): model
            for model in supported_models
        }

        if normalized_desired and normalized_desired in supported_names and normalized_desired not in exclude:
            return normalized_desired

        ranked = sorted(
            [
                name for name in supported_names
                if name not in exclude and self._is_text_generation_candidate(name)
            ],
            key=self._model_rank,
        )
        if ranked:
            return ranked[0]

        fallback = sorted([name for name in supported_names if name not in exclude])
        return fallback[0] if fallback else normalized_desired

    def _build_generate_endpoint(self, model_name: str) -> str:
        return (
            f"{self.base_url}/models/{self._normalize_model_name(model_name)}"
            f":generateContent?key={parse.quote(self.config.api_key or '')}"
        )

    def _request(self, endpoint: str, method: str, payload: dict | None = None) -> tuple[int, str]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if payload is not None else {}
        req = request.Request(endpoint, data=body, headers=headers, method=method)

        try:
            with request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                return response.status, response.read().decode("utf-8")
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            raise LLMProviderError(exc.code, details, endpoint) from exc

    @staticmethod
    def _normalize_model_name(model_name: str) -> str:
        return str(model_name or "").replace("models/", "").strip()

    @staticmethod
    def _is_text_generation_candidate(model_name: str) -> bool:
        lowered = model_name.lower()
        disallowed_tokens = ("embedding", "image", "audio", "tts", "robotics", "computer-use")
        return "gemini" in lowered and not any(token in lowered for token in disallowed_tokens)

    @staticmethod
    def _model_rank(model_name: str) -> tuple[int, str]:
        lowered = model_name.lower()
        if lowered == "gemini-flash-latest":
            return (0, lowered)
        if lowered == "gemini-2.5-flash":
            return (1, lowered)
        if lowered == "gemini-3.5-flash":
            return (2, lowered)
        if "flash-latest" in lowered:
            return (3, lowered)
        if "flash" in lowered and "preview" not in lowered and "lite" not in lowered:
            return (4, lowered)
        if "flash-lite" in lowered and "preview" not in lowered:
            return (5, lowered)
        if "pro-latest" in lowered:
            return (6, lowered)
        if "preview" in lowered:
            return (8, lowered)
        return (7, lowered)

    @staticmethod
    def _extract_text(response: GeminiGenerateContentResponse) -> str:
        parts: list[str] = []
        for candidate in response.candidates:
            if not candidate.content:
                continue
            for part in candidate.content.parts:
                if part.text:
                    parts.append(part.text)
        return "\n".join(parts).strip()
