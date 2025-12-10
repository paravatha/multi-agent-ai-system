FROM python:3.12-slim

# Define common environment variables
ENV PATH="${PATH}:/home/.local/bin"
ENV PORT=8061

# Set working directory
WORKDIR /app

# Upgrade system packages, install vim, curl, and uv, then clean up
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends vim curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create input and output directories
RUN mkdir -p /app/data/input \
    && mkdir -p /app/data/output

# Expose port
EXPOSE ${PORT}

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8061/health')" || exit 1

# Run the application
CMD ["python", "src/main.py", "--mode", "api", "--host", "0.0.0.0", "--port", "8061"]
