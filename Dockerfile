# DoChat+ - Offline AI-Powered Document Intelligence Chatbot
# Multi-stage Docker build for optimized production deployment

# Stage 1: Base image with system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Install Ollama
FROM base as ollama-installer

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Stage 3: Python dependencies
FROM base as python-deps

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 4: Final application image
FROM python-deps as final

# Copy Ollama from installer stage
COPY --from=ollama-installer /usr/local/bin/ollama /usr/local/bin/ollama

# Create non-root user for security
RUN groupadd -r dochat && useradd -r -g dochat -u 1001 dochat

# Create necessary directories
RUN mkdir -p /app/config /app/docs /app/exports /app/logs && \
    chown -R dochat:dochat /app

# Copy application files
COPY --chown=dochat:dochat app.py /app/
COPY --chown=dochat:dochat config/ /app/config/
COPY --chown=dochat:dochat README.md /app/

# Create startup script
RUN cat > /app/start.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting DoChat+ Application..."

# Start Ollama in background
echo "📦 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
sleep 10

# Check if model exists, if not pull it
MODEL_NAME=${DOCHAT_OLLAMA_MODEL:-"llama3.1:8b-instruct-q5_K_M"}
echo "🔍 Checking for model: $MODEL_NAME"

if ! ollama list | grep -q "${MODEL_NAME%:*}"; then
    echo "📥 Pulling model: $MODEL_NAME"
    ollama pull "$MODEL_NAME"
else
    echo "✅ Model $MODEL_NAME already available"
fi

# Start the main application
echo "🌟 Starting DoChat+ interface..."
python app.py

# Cleanup on exit
trap "kill $OLLAMA_PID 2>/dev/null || true" EXIT
EOF

# Make startup script executable
RUN chmod +x /app/start.sh

# Switch to non-root user
USER dochat

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Set working directory
WORKDIR /app

# Default command
CMD ["/app/start.sh"]

# Labels for metadata
LABEL maintainer="DoChat+ Team" \
      version="1.0.0" \
      description="Offline AI-Powered Document Intelligence Chatbot" \
      org.opencontainers.image.title="DoChat+" \
      org.opencontainers.image.description="Privacy-preserving PDF Q&A with LLaMA 3.1" \
      org.opencontainers.image.url="https://github.com/yourusername/dochat-plus" \
      org.opencontainers.image.documentation="https://github.com/yourusername/dochat-plus/blob/main/README.md" \
      org.opencontainers.image.source="https://github.com/yourusername/dochat-plus" \
      org.opencontainers.image.licenses="MIT"