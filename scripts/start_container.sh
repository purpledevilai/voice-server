#!/bin/bash


# Docker run
docker run -p 8000:8000 \
  --env-file .env \
  -e PYTHONUNBUFFERED=1 \
  --name voice-server-container \
  -v $(pwd)/src:/app \
  voice-server-image