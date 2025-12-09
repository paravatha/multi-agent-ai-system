#!/bin/bash
# Build and run the Docker container for the application in API mode
# docker build -t podcast-pipeline-api .

# Run the Docker container, mapping port 8061
# docker run -p 8061:8061 podcast-pipeline-api

# Alternatively, you can use docker-compose to manage the container
docker-compose up -d
