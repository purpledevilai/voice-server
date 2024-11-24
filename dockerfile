# Use the official Python image as the base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Install system dependencies required for PyTorch and Whisper
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port that Gunicorn will run on
EXPOSE 8000

# Define the command to start the Gunicorn server
CMD ["gunicorn", "-w", "1", "-k", "gthread", "--timeout", "60", "-b", "0.0.0.0:8000", "app:app"]
