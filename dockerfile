# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /film_point

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
RUN pip install watchdog

# Copy the application files to the container
COPY . /film_point/

# Set environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

CMD ["watchmedo", "auto-restart", "--patterns='*.py;*.html;*.css;.env'", "--recursive", "--", "flask", "run", "--host=0.0.0.0"]