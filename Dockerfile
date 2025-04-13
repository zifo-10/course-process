FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . /app

EXPOSE 8000

# Run the app (remove --reload for production)
CMD ["uvicorn", "wsgi:app", "--host", "0.0.0.0", "--port", "8000"]
