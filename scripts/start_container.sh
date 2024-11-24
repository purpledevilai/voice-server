#!/bin/bash


# Docker run
docker run -p 8000:8000 \
  --env-file .env \
  -e PYTHONUNBUFFERED=1 \
  --name rebin-backend-container \
  -v $(pwd):/app \
  rebin-backend-image