FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will set PORT env variable)
EXPOSE 8000

# Start command - Railway sets PORT automatically
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

