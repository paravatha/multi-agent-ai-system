from __future__ import annotations

import logging
from dataclasses import dataclass
from textwrap import dedent

from google.adk.agents import Agent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.google_search_tool import google_search

from config import Settings


@dataclass(slots=True)
class AgentBundle:
    summarizer: LlmAgent
    key_insights: LlmAgent
    search: Agent
    fact_checker: LlmAgent


class AgentFactory:
    def __init__(self, dataset_json_payload: str, settings: Settings) -> None:
        self.dataset_json_payload = dataset_json_payload
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing AgentFactory with dataset payload.")

    def build(self) -> AgentBundle:
        self.logger.info("Building agent bundle for podcast workflow.")
        try:
            summarizer = self._create_summarizer_agent()
            key_insights = self._create_key_insights_agent()
            search_agent = self._create_search_agent()
            fact_checker = self._create_fact_checker_agent(summarizer, key_insights, search_agent)
            self.logger.info("Successfully initialized agent bundle.")
            return AgentBundle(
                summarizer=summarizer,
                key_insights=key_insights,
                search=search_agent,
                fact_checker=fact_checker,
            )
        except Exception:
            self.logger.exception("Failed to build agent bundle.")
            raise

    def _create_summarizer_agent(self) -> Agent:
        self.logger.debug("Creating summarizer agent.")
        instruction = dedent(
            f"""
            You are a specialized podcast summarizer agent.
            - Your job is to analyze raw podcast data provided below in JSON format.
            - Podcast raw data: {self.dataset_json_payload}
            - Generate a summary of each episode (200–300 words) to produce a structured list of::
                • Core themes
                • Key discussions
                • Outcomes or opinions shared
            - Provide the output in a markdown section for 'Core Themes', 'Key Discussions', and 'Outcomes/Opinions'.
            """
        ).strip()
        return LlmAgent(
            name="summarizer_agent",
            model=Gemini(
                model=self.settings.gemini_flash_lite,
                retry_options=self.settings.retry_options,
            ),
            instruction=instruction,
            output_key="summarizer_agent_results",
        )

    def _create_key_insights_agent(self) -> Agent:
        self.logger.debug("Creating key insights agent.")
        instruction = dedent(
            f"""You are a specialized podcasts key insights agent.
            - Your job is to analyze raw data provided below in json format
            - Podcast raw data: {self.dataset_json_payload}.
            - You need to produce a structured list of:
            •	Top 5 takeaways
            •	Notable quotes (with timestamps)
            • Topics discussed (tag-style labels)
            - Provide the output in a markdown table format with columns for 'Takeaways', 'Quotes', and 'Topics'.
            """
        ).strip()
        return LlmAgent(
            name="key_insights_agent",
            model=self.settings.gemini_flash_lite,
            instruction=instruction,
            output_key="key_insights_agent_results",
        )

    def _create_search_agent(self) -> Agent:
        self.logger.debug("Creating search agent.")
        return Agent(
            name="search_agent",
            model=self.settings.gemini_flash_lite,
            instruction="You specialize in crafting concise Google Search queries to support fact-checking requests.",
            tools=[google_search],
        )

    def _create_fact_checker_agent(self, summarizer: Agent, key_insights: Agent, search_agent: Agent) -> Agent:
        self.logger.debug("Creating fact checker agent.")
        instruction = dedent(
            """You are a fact checker agent.
                - Include the summarizer_agent_output {summarizer_agent_results} with headline 'Summarization'
                - Include the key_insights_agent_output {key_insights_agent_results} with headline 'Key Insights'
                - Your job is to analyze the 'Summarization' and 'Key Insights' provided by other agents.
                - Identify factual statements (e.g., “NASA Mars mission launches in 2026”) and verify them using reliable external sources like google search or Wikipedia,
                - Mark each as:
                    •	✅ Verified true
                    •	⚠️ Possibly outdated/inaccurate
                    •	❓ Unverifiable
                - Here is an Example output:
                    Claim	Verification	Confidence
                    NASA’s Mars mission launches in 2026	True (confirmed by mock NASA DB)	0.92
                    Bitcoin will reach $200K by 2025	Unverifiable	0.40
                """
        ).strip()
        return LlmAgent(
            name="fact_checker_agent",
            model=self.settings.gemini_flash,
            instruction=instruction,
            output_key="fact_checker_agent_results",
            tools=[
                AgentTool(summarizer),
                AgentTool(key_insights),
                AgentTool(search_agent),
            ],
        )
