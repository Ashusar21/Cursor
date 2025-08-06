#!/bin/bash

# DoChat+ Setup Script
# Automated installation and setup for DoChat+ Document Intelligence Chatbot

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.8"
VENV_NAME="dochat_env"
OLLAMA_MODEL="llama3.1:8b-instruct-q5_K_M"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    log_info "Checking Python installation..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        log_error "Python is not installed. Please install Python ${PYTHON_MIN_VERSION}+ first."
        exit 1
    fi
    
    # Get Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        log_error "Python ${PYTHON_MIN_VERSION}+ is required. Found: ${PYTHON_VERSION}"
        exit 1
    fi
    
    log_success "Python ${PYTHON_VERSION} found"
}

# Install Ollama
install_ollama() {
    log_info "Checking Ollama installation..."
    
    if command_exists ollama; then
        log_success "Ollama is already installed"
        return 0
    fi
    
    log_info "Installing Ollama..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        log_warning "Please install Ollama manually from https://ollama.ai/download"
        read -p "Press Enter after installing Ollama..."
    fi
    
    if command_exists ollama; then
        log_success "Ollama installed successfully"
    else
        log_error "Failed to install Ollama"
        exit 1
    fi
}

# Start Ollama service
start_ollama() {
    log_info "Starting Ollama service..."
    
    # Check if Ollama is already running
    if pgrep -x "ollama" > /dev/null; then
        log_success "Ollama service is already running"
        return 0
    fi
    
    # Start Ollama in background
    ollama serve &
    OLLAMA_PID=$!
    
    # Wait for Ollama to start
    log_info "Waiting for Ollama to start..."
    sleep 5
    
    # Check if Ollama is responding
    for i in {1..10}; do
        if ollama list >/dev/null 2>&1; then
            log_success "Ollama service started successfully"
            return 0
        fi
        sleep 2
    done
    
    log_error "Failed to start Ollama service"
    exit 1
}

# Pull Ollama model
pull_model() {
    log_info "Checking for model: ${OLLAMA_MODEL}"
    
    if ollama list | grep -q "${OLLAMA_MODEL%:*}"; then
        log_success "Model ${OLLAMA_MODEL} is already available"
        return 0
    fi
    
    log_info "Pulling model: ${OLLAMA_MODEL} (this may take a while...)"
    
    if ollama pull "${OLLAMA_MODEL}"; then
        log_success "Model ${OLLAMA_MODEL} pulled successfully"
    else
        log_error "Failed to pull model ${OLLAMA_MODEL}"
        log_info "You can try a smaller model instead:"
        log_info "  ollama pull llama3.1:8b-instruct-q4_0"
        exit 1
    fi
}

# Create virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    if [ -d "${VENV_NAME}" ]; then
        log_success "Virtual environment already exists"
        return 0
    fi
    
    $PYTHON_CMD -m venv "${VENV_NAME}"
    
    if [ -d "${VENV_NAME}" ]; then
        log_success "Virtual environment created: ${VENV_NAME}"
    else
        log_error "Failed to create virtual environment"
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Activate virtual environment
    source "${VENV_NAME}/bin/activate" 2>/dev/null || source "${VENV_NAME}/Scripts/activate" 2>/dev/null
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "Python dependencies installed successfully"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating project directories..."
    
    mkdir -p docs exports logs config
    
    log_success "Project directories created"
}

# Run application
run_app() {
    log_info "Starting DoChat+ application..."
    
    # Activate virtual environment
    source "${VENV_NAME}/bin/activate" 2>/dev/null || source "${VENV_NAME}/Scripts/activate" 2>/dev/null
    
    # Start the application
    python app.py
}

# Main setup function
main() {
    echo "========================================"
    echo "🚀 DoChat+ Setup Script"
    echo "========================================"
    echo ""
    
    # Check system requirements
    check_python
    
    # Install and setup Ollama
    install_ollama
    start_ollama
    pull_model
    
    # Setup Python environment
    setup_venv
    install_dependencies
    create_directories
    
    echo ""
    log_success "Setup completed successfully!"
    echo ""
    echo "To start the application:"
    echo "  1. Activate the virtual environment:"
    echo "     source ${VENV_NAME}/bin/activate    # Linux/macOS"
    echo "     ${VENV_NAME}\\Scripts\\activate      # Windows"
    echo ""
    echo "  2. Run the application:"
    echo "     python app.py"
    echo ""
    echo "  3. Open your browser to:"
    echo "     http://localhost:7860"
    echo ""
    
    # Ask if user wants to start the app now
    read -p "Would you like to start the application now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_app
    fi
}

# Handle script interruption
trap 'echo ""; log_warning "Setup interrupted"; exit 1' INT

# Run main function
main "$@"