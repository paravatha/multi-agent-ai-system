from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict


class TranscriptLoader:
    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding
        self.logger = logging.getLogger(self.__class__.__name__)

    def load(self, path: str | Path) -> Dict[str, Any]:
        target_path = Path(path)
        self.logger.debug("Attempting to load transcript file: %s", target_path)
        if not target_path.exists():
            self.logger.error("Transcript file not found: %s", target_path)
            raise FileNotFoundError(f"Transcript file not found: {target_path}")
        try:
            with target_path.open("r", encoding=self.encoding) as file:
                data = json.load(file)
            self.logger.info("Successfully loaded transcript file: %s", target_path)
            return data
        except json.JSONDecodeError as e:
            self.logger.exception("Failed to parse JSON from file: %s", target_path)
            raise ValueError(f"Invalid JSON format in file: {target_path}") from e
        except Exception:
            self.logger.exception("Unexpected error while loading file: %s", target_path)
            raise

    @staticmethod
    def to_payload(data: Dict[str, Any]) -> str:
        logging.getLogger(TranscriptLoader.__name__).debug("Converting data to JSON payload.")
        return json.dumps(data, indent=2)
