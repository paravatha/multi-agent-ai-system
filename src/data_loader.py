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
        if not target_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {target_path}")
        with target_path.open("r", encoding=self.encoding) as file:
            data = json.load(file)
        self.logger.info("Loaded transcript file: %s", target_path)
        return data

    @staticmethod
    def to_payload(data: Dict[str, Any]) -> str:
        return json.dumps(data, indent=2)
