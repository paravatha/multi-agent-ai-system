from __future__ import annotations

import argparse
import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from config import Settings
from pipeline import PodcastAgentPipeline

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the podcast multi-agent pipeline.")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/ep002_ai_healthcare.json",
        help="Path to the podcast transcript JSON file.",
    )
    parser.add_argument(
        "--env-file",
        type=str,
        default=None,
        help="Optional path to a .env file with model credentials.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("LOG_LEVEL", "INFO"),
        help="Logging level (defaults to LOG_LEVEL env or INFO).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional file path to persist the pipeline response.",
    )
    return parser.parse_args()


def stringify_response(response: Any) -> str:
    if response is None:
        return ""
    for attr in ("output_text", "text", "content"):
        value = getattr(response, attr, None)
        if value is not None:
            return str(value)
    return str(response)


async def run_pipeline(dataset_path: Path, settings: Settings) -> Any:
    logger.info("Launching podcast agent pipeline for %s", dataset_path)
    pipeline = PodcastAgentPipeline(dataset_path=dataset_path, settings=settings)
    result = await pipeline.run()
    logger.info("Pipeline run completed.")
    return result


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "--input-dataset",
        default="data/input/ep001_remote_work.json",
        help="Input dataset",
    )

    parser.add_argument(
        "--output-folder",
        default="data/output",
        help="Output folder",
    )

    args = parser.parse_args(argv)

    dataset_path = Path(args.input_dataset)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file {args.input_dataset} not found")
    settings = Settings.from_env()

    response = asyncio.run(run_pipeline(dataset_path, settings))
    output_text = stringify_response(response)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(args.output_folder) / f"pipeline_output_{timestamp}.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")
    logger.info("Persisted pipeline output to %s", output_path)

    if output_text:
        print(output_text)


if __name__ == "__main__":
    main()
