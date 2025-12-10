from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from google.genai import types

LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"


def configure_logging(level: str = "INFO") -> None:
    logger = logging.getLogger()
    if not logger.handlers:
        logging.basicConfig(level=level, format=LOG_FORMAT)
    else:
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)


def retry_config(attempts: int = 2) -> types.HttpRetryOptions:
    return types.HttpRetryOptions(
        attempts=attempts,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )


@dataclass(slots=True)
class Settings:
    gemini_flash: str
    gemini_flash_lite: str
    retry_attempts: int
    retry_options: types.HttpRetryOptions

    @classmethod
    def from_env(cls, env_file: str | os.PathLike[str] | None = None) -> "Settings":
        if env_file:
            load_dotenv(dotenv_path=Path(env_file))
        else:
            load_dotenv()

        gemini_flash = os.getenv("GEMINI_FLASH")
        logging.info(f"{gemini_flash=}")
        gemini_flash_lite = os.getenv("GEMINI_FLASH_LITE")
        logging.info(f"{gemini_flash_lite=  }")
        attempts_raw = os.getenv("RETRY_ATTEMPTS", "3")
        try:
            attempts = max(1, int(attempts_raw))
        except ValueError as exc:
            raise RuntimeError(f"Invalid RETRY_ATTEMPTS value: {attempts_raw}") from exc
        logging.info(f"RETRY_ATTEMPTS: {attempts}")

        missing = [
            name
            for name, value in (
                ("GEMINI_FLASH", gemini_flash),
                ("GEMINI_FLASH_LITE", gemini_flash_lite),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
        # Type assertion for mypy and static checkers
        assert gemini_flash is not None
        assert gemini_flash_lite is not None
        return cls(
            gemini_flash=gemini_flash,
            gemini_flash_lite=gemini_flash_lite,
            retry_attempts=attempts,
            retry_options=retry_config(attempts),
        )
