# Use a Python base image
FROM python:3.11-slim

# Install system dependencies (needed for compiling some packages if binary is not available, and curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the official installer or by copying from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy lockfiles and configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies of the main project
# --frozen ensures we use the exact lockfile versions
RUN uv sync --frozen --no-dev

# Copy the rest of the codebase (including mcp_servers, scripts, etc.)
COPY . .

# Pre-sync the MCP server dependencies so they don't delay the first request
# This ensures that `uv run` inside the backend will start instantly
RUN cd mcp_servers/pubmed_server && uv sync --frozen --no-dev
RUN cd mcp_servers/drugdata_server && uv sync --frozen --no-dev
RUN cd mcp_servers/vectorstore_server && uv sync --frozen --no-dev

# Build-time generation of the Chroma database
RUN uv run python scripts/ingest_kb.py

# Expose the API port (default FastAPI port, overridden by PORT environment variable)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Make start.sh executable
RUN chmod +x start.sh

# Start the unified services
CMD ["./start.sh"]
