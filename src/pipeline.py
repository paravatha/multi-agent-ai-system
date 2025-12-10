from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from google.adk.agents import SequentialAgent
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
        self.logger.debug("Initializing PodcastAgentPipeline with dataset: %s", dataset_path)
        self.settings = settings
        self.dataset_path = Path(dataset_path)
        self.loader = loader or TranscriptLoader()

        try:
            self.dataset = self.loader.load(self.dataset_path)
            self.dataset_payload = self.loader.to_payload(self.dataset)
            self.agents: AgentBundle = AgentFactory(self.dataset_payload, self.settings).build()
            self.logger.info("Pipeline initialized successfully for dataset: %s", self.dataset_path)
        except Exception:
            self.logger.exception("Failed to initialize pipeline for dataset: %s", self.dataset_path)
            raise

    def build_prompt(self) -> str:
        self.logger.debug("Building prompt for pipeline execution.")
        prompt = """
                - Generate a comprehensive analysis of the podcast episode data provided
                - Return the response in a human-readable format.
                """
        return prompt

    async def run(self) -> Any:
        self.logger.info("Starting pipeline execution for dataset: %s", self.dataset_path)
        try:
            podcast_agent_pipeline = SequentialAgent(
                name="podcast_agent_pipeline",
                sub_agents=[self.agents.summarizer, self.agents.key_insights, self.agents.fact_checker],
            )
            runner = InMemoryRunner(agent=podcast_agent_pipeline)
            response = await runner.run_debug(self.build_prompt())
            self.logger.info("podcast_agent_pipeline execution completed successfully.")
            return response
        except Exception:
            self.logger.exception("Pipeline execution failed for dataset: %s", self.dataset_path)
            raise
