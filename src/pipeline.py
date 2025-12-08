from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from google.adk.runners import InMemoryRunner

from agents import AgentBundle, AgentFactory
from config import Settings
from data_loader import TranscriptLoader


class PodcastAgentPipeline:
    def __init__(
        self,
        dataset_path: str | Path,
        settings: Settings,
        loader: TranscriptLoader | None = None,
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = settings
        self.dataset_path = Path(dataset_path)
        self.loader = loader or TranscriptLoader()

        self.dataset = self.loader.load(self.dataset_path)
        self.dataset_payload = self.loader.to_payload(self.dataset)
        self.agents: AgentBundle = AgentFactory(self.dataset_payload, self.settings).build()

    def build_prompt(self) -> str:
        return (
            f"Use {self.dataset_payload} to analyze the podcast episode data.\n"
            " - Summarize the episode content.\n"
            " - Extract key insights including top takeaways, notable quotes, and topics discussed.\n"
            " - Fact-check significant claims made in the episode using external sources.\n"
            " - Provide a markdown table summarizing:\n"
            "   • Episode summaries\n"
            "   • Key insights\n"
            "   • Fact-checking results\n"
            " - Return the response in a human-readable format."
        )

    async def run(self) -> Any:
        self.logger.info("Starting pipeline execution for dataset: %s", self.dataset_path)
        runner = InMemoryRunner(agent=self.agents.fact_checker)
        response = await runner.run_debug(self.build_prompt())
        self.logger.info("Pipeline execution completed.")
        return response
