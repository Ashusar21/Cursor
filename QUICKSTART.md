# 🚀 DoChat+ Quick Start Guide

Get up and running with DoChat+ in 5 minutes!

## Prerequisites

- Python 3.8+
- 4GB+ RAM (8GB recommended)
- Internet connection for initial setup

## Option 1: Automated Setup (Recommended)

```bash
# Make setup script executable and run
chmod +x setup.sh
./setup.sh
```

The script will:
1. ✅ Check Python installation
2. 📦 Install Ollama
3. 🤖 Download LLaMA 3.1 model
4. 🐍 Set up Python environment
5. 📚 Install dependencies
6. 🚀 Start the application

## Option 2: Manual Setup

### 1. Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/download
```

### 2. Pull the Model

```bash
ollama pull llama3.1:8b-instruct-q5_K_M
```

### 3. Setup Python Environment

```bash
# Create virtual environment
python -m venv dochat_env

# Activate it
source dochat_env/bin/activate  # Linux/macOS
# or
dochat_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

## Option 3: Docker (One-liner)

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Access the Application

Once running, open your browser to:
**http://localhost:7860**

## First Steps

1. **Upload a PDF**: Click "📁 Upload PDF Document"
2. **Wait for Processing**: The system builds the search index
3. **Ask Questions**: Type questions about your document
4. **Try Summarization**: Switch to "Summarize" mode
5. **Export Results**: Download your chat history

## Example Queries

- "What are the main findings of this document?"
- "Summarize the methodology section"
- "What are the key recommendations?"
- "Compare the pros and cons mentioned"
- "Find information about [specific topic]"

## Troubleshooting

### Common Issues

**"Model not found"**
```bash
ollama pull llama3.1:8b-instruct-q5_K_M
```

**"Ollama not running"**
```bash
ollama serve
```

**"Port already in use"**
```bash
# Change port in config/settings.py
SERVER_PORT = 7861
```

**Memory issues**
- Use smaller model: `ollama pull llama3.1:8b-instruct-q4_0`
- Reduce chunk size in `config/settings.py`

### Getting Help

- 📖 Read the full [README.md](README.md)
- 🐛 Report issues on GitHub
- 💬 Check configuration in `config/settings.py`

## Next Steps

- Customize settings in `config/settings.py`
- Try different models (see README for options)
- Explore Docker deployment
- Set up for production use

---

**Happy document chatting! 🎉**