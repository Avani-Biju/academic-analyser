from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import load_environment
from app.llm.client import GeminiClient


def main() -> None:
    load_environment()
    client = GeminiClient()

    if not client.is_available():
        print("model used: none")
        print("http status: n/a")
        print("response: GEMINI_API_KEY is not configured")
        print("elapsed time: 0.00s")
        return

    started = time.perf_counter()
    try:
        result = client.generate_text("Reply only with OK")
        elapsed = time.perf_counter() - started
        print(f"model used: {result['model']}")
        print(f"http status: {result['status_code']}")
        print(f"response: {result['response_text']}")
        print(f"elapsed time: {elapsed:.2f}s")
    except Exception as exc:
        elapsed = time.perf_counter() - started
        print(f"model used: {client.config.model}")
        print("http status: error")
        print(f"response: {exc}")
        print(f"elapsed time: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
