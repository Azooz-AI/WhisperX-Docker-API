# Use NVIDIA CUDA base image with Python 3.10
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    ffmpeg \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install PyTorch with CUDA support first (this is important for GPU acceleration)
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Install WhisperX
RUN pip install whisperx

# Copy application files
COPY . .

# Create cache directory for models
RUN mkdir -p /.cache && chmod 777 /.cache

# Model will be downloaded automatically on first API request
# This makes the build faster and the image smaller

# Expose port
EXPOSE 5772

# Set default timeout (20 minutes = 1200 seconds)
ENV TIMEOUT_SECONDS=1200

# Run the Flask application
CMD ["python", "app.py"]