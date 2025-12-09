from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import Settings
from pipeline import PodcastAgentPipeline

logger = logging.getLogger(__name__)

# FastAPI application
app = FastAPI(title="Podcast Multi-Agent Pipeline API")


class PipelineRequest(BaseModel):
    """Request model for pipeline execution."""

    dataset_path: str = Field(..., description="Path to the podcast transcript JSON file")
    output_folder: str | None = Field(None, description="Optional output folder path")

    model_config = {"json_schema_extra": {"example": {"dataset_path": "data/input/ep001_remote_work.json", "output_folder": "data/output"}}}


class PipelineResponse(BaseModel):
    """Response model for pipeline execution."""

    output_text: str
    output_path: str | None = None
    timestamp: str


def stringify_response(response: Any) -> str:
    if response is None:
        return ""
    if response and hasattr(response[0], "content") and hasattr(response[0].content, "parts"):
        text = response[0].content.parts[0].text
        logger.info("Extracted Text: %s", text)
    return str(text)


async def run_pipeline(dataset_path: Path, settings: Settings) -> Any:
    logger.info("Launching podcast agent pipeline for %s", dataset_path)
    pipeline = PodcastAgentPipeline(dataset_path=dataset_path, settings=settings)
    result = await pipeline.run()
    logger.info("Pipeline run completed.")
    return result


@app.post("/run-pipeline", response_model=PipelineResponse)
async def run_pipeline_endpoint(request: PipelineRequest) -> PipelineResponse:
    """
    Execute the podcast multi-agent pipeline.

    Args:
        request: Pipeline execution request with dataset path and optional output folder

    Returns:
        PipelineResponse with output text and metadata
    """
    dataset_path = Path(request.dataset_path)
    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset file {request.dataset_path} not found")

    try:
        settings = Settings.from_env()
        response = await run_pipeline(dataset_path, settings)
        output_text = stringify_response(response)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = None

        if request.output_folder:
            output_folder = Path(request.output_folder)
            output_file_path = output_folder / f"pipeline_output_{timestamp}.md"
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            output_file_path.write_text(output_text, encoding="utf-8")
            output_path = str(output_file_path)
            logger.info("Persisted pipeline output to %s", output_path)

        return PipelineResponse(output_text=output_text, output_path=output_path, timestamp=timestamp)
    except Exception as e:
        logger.exception("Pipeline execution failed")
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point for backward compatibility."""
    parser = argparse.ArgumentParser(description="Run podcast pipeline via CLI or start API server")

    parser.add_argument("--mode", choices=["cli", "api"], default="cli", help="Run mode: 'cli' for direct execution, 'api' to start FastAPI server")

    parser.add_argument(
        "--input-dataset",
        default="data/input/ep001_remote_work.json",
        help="Input dataset (CLI mode only)",
    )

    parser.add_argument(
        "--output-folder",
        default="data/output",
        help="Output folder (CLI mode only)",
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (API mode only)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (API mode only)",
    )

    args = parser.parse_args(argv)

    if args.mode == "api":
        import uvicorn

        uvicorn.run(app, host=args.host, port=args.port)
    else:
        # CLI mode
        dataset_path = Path(args.input_dataset)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset file {args.input_dataset} not found")
        settings = Settings.from_env()

        response = asyncio.run(run_pipeline(dataset_path, settings))
        output_text = stringify_response(response)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(args.output_folder) / f"pipeline_output_{timestamp}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_text, encoding="utf-8")
        logger.info("Persisted pipeline output to %s", output_path)

        if output_text:
            logger.info(output_text)


if __name__ == "__main__":
    main()
