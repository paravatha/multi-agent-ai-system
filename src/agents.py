from __future__ import annotations

import logging
from dataclasses import dataclass
from textwrap import dedent

from google.adk.agents import Agent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool, google_search

from config import Settings


@dataclass(slots=True)
class AgentBundle:
    summarizer: LlmAgent
    key_insights: LlmAgent
    search: Agent
    fact_checker: LlmAgent


class AgentFactory:
    def __init__(self, dataset_payload: str, settings: Settings) -> None:
        self.dataset_payload = dataset_payload
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)

    def build(self) -> AgentBundle:
        summarizer = self._create_summarizer_agent()
        key_insights = self._create_key_insights_agent()
        search_agent = self._create_search_agent()
        fact_checker = self._create_fact_checker_agent(summarizer, key_insights, search_agent)
        self.logger.info("Initialized agent bundle for podcast workflow.")
        return AgentBundle(
            summarizer=summarizer,
            key_insights=key_insights,
            search=search_agent,
            fact_checker=fact_checker,
        )

    def _create_summarizer_agent(self) -> Agent:
        instruction = dedent(
            f"""
            You are a specialized podcast summarizer agent.
            - Your job is to analyze raw podcast data provided below in JSON format.
            - Podcast raw data: {self.dataset_payload}
            - Generate a summary of each episode (200–300 words) that captures:
                • Core themes
                • Key discussions
                • Outcomes or opinions shared
            - Provide the output in a markdown table format with columns for 'Core Themes', 'Key Discussions', and 'Outcomes/Opinions'.
            """
        ).strip()
        return LlmAgent(
            name="summarizer_agent",
            model=Gemini(
                model=self.settings.gemini_model_flash,
                retry_options=self.settings.retry_options,
            ),
            instruction=instruction,
        )

    def _create_key_insights_agent(self) -> Agent:
        instruction = dedent(
            f"""
            You are a specialized podcasts key insights agent.
            - Your job is to analyze raw podcast data provided below in JSON format.
            - Podcast raw data: {self.dataset_payload}
            - Produce a structured list of:
                • Top 5 takeaways
                • Notable quotes (with timestamps)
                • Topics discussed (tag-style labels)
            - Provide the output in a markdown table format with columns for 'Takeaways', 'Quotes', and 'Topics'.
            """
        ).strip()
        return LlmAgent(
            name="key_insights_agent",
            model=self.settings.gemini_model_flash,
            instruction=instruction,
            output_key="key_insights_agent_results",
        )

    def _create_search_agent(self) -> Agent:
        return Agent(
            name="search_agent",
            model=self.settings.gemini_model_flash,
            instruction="You specialize in crafting concise Google Search queries to support fact-checking requests.",
            tools=[google_search],
        )

    def _create_fact_checker_agent(self, summarizer: Agent, key_insights: Agent, search_agent: Agent) -> Agent:
        instruction = dedent(
            """
            You are a fact checker agent.
            - Analyze the summarized podcast data and key insights provided by other agents.
            - Identify factual statements and verify them using reliable external sources such as Google Search or Wikipedia.
            - Mark each statement as:
                • ✅ Verified true
                • ⚠️ Possibly outdated/inaccurate
                • ❓ Unverifiable
            - Present results in a markdown table with columns for claim, verification status, and confidence (0-1 scale).
            """
        ).strip()
        return LlmAgent(
            name="fact_checker_agent",
            model=self.settings.gemini_model_pro,
            instruction=instruction,
            output_key="fact_checker_agent_results",
            tools=[
                AgentTool(summarizer),
                AgentTool(key_insights),
                AgentTool(search_agent),
            ],
        )
