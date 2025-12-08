# multi-agent-ai-system

## Overview

Agentic AI workflow that helps an ad agency manage podcast content by summarizing episodes, extracting key notes, and fact-checking notable claims. The solution now uses a modular Python package under `src/multi_agent` to keep configuration, data loading, agent assembly, and orchestration maintainable.

## Project Structure

- `src/multi_agent/config.py` — Environment-aware settings and logging bootstrap.
- `src/multi_agent/data_loader.py` — Transcript loading utilities.
- `src/multi_agent/agents.py` — Factory that wires up summarizer, insights, search, and fact-checker agents.
- `src/multi_agent/pipeline.py` — Async pipeline that runs the agent bundle via `InMemoryRunner`.
- `notebooks/multi-agent-system.ipynb` — Minimal notebook that demonstrates the pipeline.

## Usage

1. Set `GEMINI_MODEL_FLASH` and `GEMINI_MODEL_PRO` in a `.env` file.
2. Install dependencies and launch Jupyter.
3. Open `notebooks/multi-agent-system.ipynb` and run the cells; adjust `dataset_path` as needed.

## Outputs

Running the pipeline yields:
- Episode summary table (200–300 words).
- Key takeaways, quotes with timestamps, and topic tags.
- Markdown fact-check table with verification status and confidence scores.
- Console logs capturing pipeline steps for traceability.
