# ============================================================
# Student Database Backend — Dockerfile
# ============================================================
# This builds an image containing:
#   - Python 3.11 (slim variant)
#   - System libraries needed by MySQL client and Chroma
#   - All Python dependencies from requirements.txt
#   - The application code
# ============================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed by:
#   - default-libmysqlclient-dev, gcc: for building any native DB drivers
#   - build-essential: general C compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first — this layer is cached unless requirements change
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ ./app/
COPY tests/ ./tests/

# Create a folder for Chroma's persistent data inside the container
RUN mkdir -p /app/chroma_data

# Expose the FastAPI port
EXPOSE 8000

# Health check — hits the API root
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the FastAPI app via uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]