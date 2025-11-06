FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt

# Verify requirements.txt exists and install dependencies
RUN echo "Checking requirements.txt..." && \
    ls -la /app/requirements.txt && \
    cat /app/requirements.txt && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    echo "Verifying installations..." && \
    pip list | grep -i fastapi && \
    pip list | grep -i uvicorn

# Copy application code
COPY . /app

# Expose port
EXPOSE 8000

# Start command (PORT will be set by Railway as environment variable)
CMD sh -c "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"

