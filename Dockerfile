# Use an official Python base image
FROM python:3.10-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and source
COPY app.py ./

# Install Python dependencies
RUN pip install --no-cache-dir gradio pypdf langchain sentence-transformers faiss-cpu python-docx

# (Optional) Download HuggingFace model for offline use
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# (Optional) Download Ollama model (if possible)
# You may need to run Ollama separately and mount its model directory

# Expose Gradio default port
EXPOSE 7860

# Run the app
CMD ["python", "app.py"]