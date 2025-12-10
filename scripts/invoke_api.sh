# !/bin/bash

# Example of how to trigger the pipeline via API for app running on localhost:8060
# curl -X POST "http://localhost:8060/run-pipeline" \
#   -H "Content-Type: application/json" \
#   -d '{"dataset_path": "data/input/ep001_remote_work.json", "output_folder": "data/output"}'

# Example of how to trigger the pipeline via API for app running on using docker container on localhost:8061

curl -X POST "http://localhost:8061/run-pipeline" \
  -H "Content-Type: application/json" \
  -d '{"dataset_path": "data/input/ep002_ai_healthcare.json", "output_folder": "data/output"}'
