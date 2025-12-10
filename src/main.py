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

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
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
        logger.warning("Received an empty response from the pipeline.")
        return ""
    final_md_text = ""
    for element in response:
        # print("Event Type:", type(element))
        # print(element.__dict__)
        content = getattr(element, "content", None)
        parts = getattr(content, "parts", None) if content is not None else None
        if parts and len(parts) > 0 and hasattr(parts[0], "text"):
            text = parts[0].text
            if text:
                final_md_text += "\n\n" + text
    return final_md_text


async def run_pipeline(dataset_path: Path, settings: Settings) -> Any:
    logger.info("Starting podcast agent pipeline for dataset: %s", dataset_path)
    try:
        pipeline = PodcastAgentPipeline(dataset_path=dataset_path, settings=settings)
        result = await pipeline.run()
        logger.info("Pipeline execution completed successfully for dataset: %s", dataset_path)
        return result
    except Exception:
        logger.exception("Error occurred while running the pipeline for dataset: %s", dataset_path)
        raise


@app.post("/run-pipeline", response_model=PipelineResponse)
async def run_pipeline_endpoint(request: PipelineRequest) -> PipelineResponse:
    """
    Execute the podcast multi-agent pipeline.

    Args:
        request: Pipeline execution request with dataset path and optional output folder

    Returns:
        PipelineResponse with output text and metadata
    """
    logger.info("Received pipeline execution request: %s", request.dict())
    dataset_path = Path(request.dataset_path)
    if not dataset_path.exists():
        logger.error("Dataset file not found: %s", request.dataset_path)
        raise HTTPException(status_code=404, detail=f"Dataset file {request.dataset_path} not found")

    try:
        settings = Settings.from_env()
        logger.debug("Loaded settings: %s", settings)
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
            logger.info("Persisted pipeline output to: %s", output_path)

        logger.info("Pipeline execution completed successfully.")
        return PipelineResponse(output_text=output_text, output_path=output_path, timestamp=timestamp)
    except Exception as e:
        logger.exception("Pipeline execution failed for request: %s", request.dict())
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check endpoint called.")
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
        logger.info("Starting FastAPI server on %s:%d", args.host, args.port)
        import uvicorn

        uvicorn.run(app, host=args.host, port=args.port)
    else:
        # CLI mode
        logger.info("Running pipeline in CLI mode with dataset: %s", args.input_dataset)
        dataset_path = Path(args.input_dataset)
        if not dataset_path.exists():
            logger.error("Dataset file not found: %s", args.input_dataset)
            raise FileNotFoundError(f"Dataset file {args.input_dataset} not found")
        settings = Settings.from_env()
        logger.debug("Loaded settings: %s", settings)

        try:
            response = asyncio.run(run_pipeline(dataset_path, settings))
            output_text = stringify_response(response)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(args.output_folder) / f"pipeline_output_{timestamp}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output_text, encoding="utf-8")
            logger.info("Persisted pipeline output to: %s", output_path)

            if output_text:
                logger.info("Pipeline output: %s", output_text)
        except Exception:
            logger.exception("Pipeline execution failed in CLI mode.")
            raise


if __name__ == "__main__":
    main()
