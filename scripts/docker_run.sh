#!/bin/bash
# Build and run the Docker container for the application in API mode
# docker build -t podcast-pipeline-api .

# Run the Docker container, mapping port 8061
# docker run -p 8061:8061 podcast-pipeline-api

# Alternatively, you can use docker-compose to manage the container
timestamp=$(date +"%Y%m%d_%H%M%S")
logfile="logs/docker_run_$timestamp.log"
echo "Starting Docker container for podcast pipeline API. Logs will be saved to $logfile"

# docker
docker-compose up --build -d
docker-compose logs -f 2>&1 | tee "$logfile"
