# Use the official Python slim image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies and libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv for virtual environment (if not already in requirements.txt)
RUN pip install --upgrade pip

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose the port FastAPI runs on
EXPOSE 8000

# Define the command to run your FastAPI app using Uvicorn
CMD ["uvicorn", "wsgi:app", "--host", "0.0.0.0", "--port", "8000"]
