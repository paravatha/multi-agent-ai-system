# multi-agent-ai-system

## Overview

- Agentic AI workflow that helps an ad agency manage podcast content by summarizing episodes, extracting key notes, and fact-checking notable claims.
- The solution uses a modular Python package under `src/` to keep configuration, data loading, agent assembly, and orchestration maintainable.

## Project Structure

- `src/config.py` — Environment-aware settings and logging bootstrap.
- `src/data_loader.py` — Transcript loading utilities.
- `src/agents.py` — Factory that wires up summarizer, insights, search, and fact-checker agents.
- `src/pipeline.py` — Async pipeline that runs the agent bundle via `SequentialAgent` and `InMemoryRunner`.
- `src/main.py` — FastAPI app and CLI entry point for running the pipeline.
- `scripts/app_run.sh` — Script to run the FastAPI server locally.
- `scripts/docker_run.sh` — Script to build and run the application in a Docker container.

## Features

- **Summarization**: Generates a structured summary of podcast episodes.
- **Key Insights Extraction**: Extracts top takeaways, notable quotes, and topics discussed.
- **Fact-Checking**: Verifies claims using external sources and provides confidence scores.
- **FastAPI Integration**: Exposes the pipeline as a REST API for programmatic access.
- **CLI Support**: Allows running the pipeline directly from the command line.

## Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-repo/multi-agent-ai-system.git
   cd multi-agent-ai-system
   ```

2. **Set Environment Variables**:
   Create a `.env` file in the root directory with the following variables:

   ```env
   GEMINI_MODEL_FLASH=your_gemini_flash_model
   GEMINI_MODEL_PRO=your_gemini_pro_model
   ```

3. **Install Dependencies**:
   Use `pip` to install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### 1. **Run the FastAPI Server**

   Start the FastAPI server to expose the pipeline as an API:

   ```bash
   python src/main.py --mode api --host 0.0.0.0 --port 8000
   ```

- Open the API documentation at: [http://localhost:8000/docs](http://localhost:8000/docs)
- Example API request:

     ```bash
     curl -X POST "http://localhost:8000/run-pipeline" \
       -H "Content-Type: application/json" \
       -d '{"dataset_path": "data/input/ep001_remote_work.json", "output_folder": "data/output"}'
     ```

### 2. **Run the Pipeline via CLI**

   Execute the pipeline directly from the command line:

   ```bash
   python src/main.py --mode cli --input-dataset data/input/ep001_remote_work.json --output-folder data/output
   ```

- The output will be saved in the specified `output-folder` with a timestamped filename.

### 3. **Run Using `scripts/app_run.sh`**

   Use the provided script to start the FastAPI server:

   ```bash
   ./scripts/app_run.sh
   ```

- This script runs the FastAPI server with default settings (`host=0.0.0.0`, `port=8000`).

### 4. **Run Using `scripts/docker_run.sh`**

   Use the provided script to build and run the application in a Docker container:

   ```bash
   ./scripts/docker_run.sh
   ```

- This script builds the Docker image and runs the container, exposing the FastAPI server on port `8000`.
- Example API request (after running the script):

     ```bash
     curl -X POST "http://localhost:8000/run-pipeline" \
       -H "Content-Type: application/json" \
       -d '{"dataset_path": "data/input/ep001_remote_work.json", "output_folder": "data/output"}'
     ```

## Outputs

Running the pipeline yields:

- **Episode Summary**: A structured summary of the podcast episode (200–300 words).
- **Key Insights**: Top takeaways, notable quotes with timestamps, and topic tags.
- **Fact-Check Table**: A markdown table with verification status and confidence scores.
- **Logs**: Detailed logs capturing pipeline steps for traceability.

## Development

### Logging

The application uses Python's `logging` module for detailed traceability. Logs include:

- Pipeline initialization and execution steps.
- Agent creation and execution details.
- Errors and exceptions with stack traces.

### Testing

To test the pipeline, use the provided dataset or create your own JSON transcript file. Ensure the file follows the expected schema.

### Example Dataset

Place your dataset in the `data/input/` directory. Example:

```json
{
  "episode_title": "The Future of Remote Work",
  "transcript": "In this episode, we discuss the future of remote work..."
}
```

## Next steps

### Deployment strategy

[Deployment.md](Deployment.md)

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License.
