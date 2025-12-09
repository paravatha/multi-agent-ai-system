# !/bin/bash
# Run the application in API mode
python src/main.py --mode api --host 0.0.0.0 --port 8060

# Example of how to trigger the pipeline via API
curl -X POST "http://localhost:8060/run-pipeline" \
  -H "Content-Type: application/json" \
  -d '{"dataset_path": "data/input/ep001_remote_work.json", "output_folder": "data/output"}'

# To run in CLI mode, uncomment the following line:
# python src/main.py --mode cli --dataset_path data/input/ep001_remote_work.json --output_folder data/output
