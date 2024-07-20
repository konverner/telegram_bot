# Use an official Python runtime as a parent image
FROM python:3.10-slim
MAINTAINER Konstantin Verner <konst.verner@gmail.com>

# Set the working directory in the container to /app
WORKDIR /app

# Copy the pyproject.toml and other necessary files
COPY pyproject.toml .
COPY src ./src
COPY tests ./tests

# Install build dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install optional dependencies if needed
RUN pip install --no-cache-dir ".[all]"

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the application when the container launches
CMD ["python", "src/telegram_bot/main.py"]