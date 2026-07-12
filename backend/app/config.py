from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_ENV_LOADED = False


def load_environment() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=False)
    logger.info("Environment loaded from %s", env_path)
    _ENV_LOADED = True
