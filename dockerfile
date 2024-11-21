# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies required for mysqlclient and cleanup after installation
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libmariadb-dev \
    inotify-tools && \
    rm -rf /var/lib/apt/lists/*  # Clean up apt cache

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application files to the container
COPY . /app/

# Set environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

