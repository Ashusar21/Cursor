"""
DoChat+ Configuration Settings

This file contains all configurable parameters for the DoChat+ application.
Modify these settings to customize the behavior of your document intelligence chatbot.
"""

import os
from pathlib import Path

# ======================
# APPLICATION SETTINGS
# ======================

# Application metadata
APP_NAME = "DoChat+"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Offline AI-Powered Document Intelligence Chatbot"

# Server configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 7860
ENABLE_QUEUE = True
SHARE_GRADIO = False

# ======================
# MODEL SETTINGS
# ======================

# Ollama LLM Configuration
OLLAMA_MODEL = "llama3.1:8b-instruct-q5_K_M"
OLLAMA_TEMPERATURE = 0.2
OLLAMA_TIMEOUT = 60

# Alternative models (uncomment to use)
# OLLAMA_MODEL = "llama3.1:70b-instruct-q4_K_M"  # Larger, more capable
# OLLAMA_MODEL = "llama3.1:8b-instruct-q4_0"     # Faster, less memory
# OLLAMA_MODEL = "mistral:7b-instruct-v0.3-q5_K_M"  # Alternative model

# Embedding Model Configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"  # Use "cuda" if you have GPU support
NORMALIZE_EMBEDDINGS = True

# Alternative embedding models (uncomment to use)
# EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"      # Better quality, slower
# EMBEDDING_MODEL_NAME = "paraphrase-MiniLM-L6-v2"  # Good for paraphrasing

# ======================
# RAG SETTINGS
# ======================

# Text Chunking Configuration
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
CHUNK_SEPARATORS = ["\n\n", "\n", " ", ""]

# Vector Search Configuration
RETRIEVAL_K = 4          # Number of chunks to retrieve
RETRIEVAL_FETCH_K = 8    # Number of chunks to fetch before MMR
MMR_LAMBDA = 0.5         # MMR diversity parameter (0=diversity, 1=relevance)

# QA Chain Configuration
CHAIN_TYPE = "stuff"     # Options: "stuff", "map_reduce", "refine", "map_rerank"
RETURN_SOURCE_DOCS = True
VERBOSE_CHAIN = True

# ======================
# UI SETTINGS
# ======================

# Gradio Interface Configuration
GRADIO_THEME = "soft"    # Options: "default", "soft", "monochrome"
MAX_FILE_SIZE_MB = 50    # Maximum PDF file size in MB
CHATBOT_HEIGHT = 400     # Height of chat interface in pixels
PREVIEW_LINES = 10       # Number of lines in preview text box

# PDF Preview Configuration
PDF_PREVIEW_HEIGHT = "600px"
PDF_PREVIEW_WIDTH = "100%"

# ======================
# EXPORT SETTINGS
# ======================

# Export Configuration
EXPORT_FORMATS = ["txt", "json"]  # Available export formats
EXPORT_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
EXPORT_DIRECTORY = "exports"

# ======================
# LOGGING SETTINGS
# ======================

# Logging Configuration
LOG_LEVEL = "INFO"        # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/dochat.log"
MAX_LOG_SIZE_MB = 10      # Maximum log file size before rotation
BACKUP_COUNT = 5          # Number of backup log files to keep

# ======================
# ADVANCED SETTINGS
# ======================

# Performance Settings
ENABLE_MEMORY_OPTIMIZATION = True
BATCH_SIZE = 32           # Batch size for embedding generation
MAX_CONCURRENT_REQUESTS = 4

# Security Settings
ALLOWED_FILE_TYPES = [".pdf"]
SANITIZE_FILENAMES = True
MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50MB in bytes

# Feature Flags
ENABLE_OCR = False        # Enable OCR for scanned PDFs (requires tesseract)
ENABLE_MULTIMODAL = False # Enable image processing (future feature)
ENABLE_API_MODE = False   # Enable REST API endpoints (future feature)

# ======================
# DIRECTORY PATHS
# ======================

# Project directories
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
EXPORTS_DIR = PROJECT_ROOT / "exports"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIG_DIR = PROJECT_ROOT / "config"

# Ensure directories exist
for directory in [DOCS_DIR, EXPORTS_DIR, LOGS_DIR, CONFIG_DIR]:
    directory.mkdir(exist_ok=True)

# ======================
# ENVIRONMENT OVERRIDES
# ======================

# Allow environment variables to override settings
OLLAMA_MODEL = os.getenv("DOCHAT_OLLAMA_MODEL", OLLAMA_MODEL)
EMBEDDING_MODEL_NAME = os.getenv("DOCHAT_EMBEDDING_MODEL", EMBEDDING_MODEL_NAME)
SERVER_HOST = os.getenv("DOCHAT_HOST", SERVER_HOST)
SERVER_PORT = int(os.getenv("DOCHAT_PORT", SERVER_PORT))
LOG_LEVEL = os.getenv("DOCHAT_LOG_LEVEL", LOG_LEVEL)

# ======================
# VALIDATION
# ======================

def validate_config():
    """Validate configuration settings."""
    errors = []
    
    # Validate chunk settings
    if CHUNK_SIZE <= CHUNK_OVERLAP:
        errors.append("CHUNK_SIZE must be greater than CHUNK_OVERLAP")
    
    # Validate retrieval settings
    if RETRIEVAL_K > RETRIEVAL_FETCH_K:
        errors.append("RETRIEVAL_K must be less than or equal to RETRIEVAL_FETCH_K")
    
    # Validate MMR lambda
    if not 0 <= MMR_LAMBDA <= 1:
        errors.append("MMR_LAMBDA must be between 0 and 1")
    
    # Validate file size
    if MAX_FILE_SIZE_MB <= 0:
        errors.append("MAX_FILE_SIZE_MB must be positive")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return True

# Validate configuration on import
if __name__ != "__main__":
    validate_config()