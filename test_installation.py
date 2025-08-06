#!/usr/bin/env python3
"""
DoChat+ Installation Test Script

This script verifies that all dependencies are properly installed
and the system is ready to run DoChat+.
"""

import sys
import subprocess
import importlib
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{message}{Colors.END}")
    print("=" * len(message))

def check_python_version():
    """Check if Python version meets requirements."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_required_packages():
    """Check if all required packages are installed."""
    print_header("Checking Required Packages")
    
    required_packages = [
        ('gradio', 'Gradio web interface'),
        ('pypdf', 'PDF processing'),
        ('sentence_transformers', 'Sentence embeddings'),
        ('transformers', 'Transformer models'),
        ('torch', 'PyTorch'),
        ('faiss', 'Vector search (faiss-cpu)'),
        ('numpy', 'Numerical computing'),
        ('langchain', 'LangChain framework'),
        ('langchain_community', 'LangChain community'),
        ('langchain_core', 'LangChain core'),
    ]
    
    all_installed = True
    
    for package, description in required_packages:
        try:
            # Handle special cases
            if package == 'faiss':
                importlib.import_module('faiss')
            else:
                importlib.import_module(package)
            print_success(f"{package} - {description}")
        except ImportError:
            print_error(f"{package} - {description} (NOT INSTALLED)")
            all_installed = False
    
    return all_installed

def check_ollama():
    """Check if Ollama is installed and running."""
    print_header("Checking Ollama")
    
    try:
        # Check if ollama command exists
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"Ollama installed - {version}")
            
            # Check if Ollama is running
            try:
                result = subprocess.run(['ollama', 'list'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print_success("Ollama service is running")
                    
                    # Check for required model
                    if 'llama3.1' in result.stdout:
                        print_success("LLaMA 3.1 model found")
                        return True
                    else:
                        print_warning("LLaMA 3.1 model not found")
                        print_info("Run: ollama pull llama3.1:8b-instruct-q5_K_M")
                        return False
                else:
                    print_error("Ollama service not responding")
                    print_info("Run: ollama serve")
                    return False
            except subprocess.TimeoutExpired:
                print_error("Ollama service check timed out")
                return False
        else:
            print_error("Ollama not working properly")
            return False
            
    except FileNotFoundError:
        print_error("Ollama not installed")
        print_info("Install from: https://ollama.ai/download")
        return False
    except subprocess.TimeoutExpired:
        print_error("Ollama check timed out")
        return False

def check_project_structure():
    """Check if project structure is correct."""
    print_header("Checking Project Structure")
    
    required_files = [
        ('app.py', 'Main application'),
        ('requirements.txt', 'Dependencies'),
        ('config/settings.py', 'Configuration'),
        ('README.md', 'Documentation'),
    ]
    
    required_dirs = [
        ('config', 'Configuration directory'),
        ('docs', 'Documentation directory'),
        ('exports', 'Exports directory'),
        ('logs', 'Logs directory'),
    ]
    
    all_present = True
    
    for file_path, description in required_files:
        if Path(file_path).exists():
            print_success(f"{file_path} - {description}")
        else:
            print_error(f"{file_path} - {description} (MISSING)")
            all_present = False
    
    for dir_path, description in required_dirs:
        if Path(dir_path).is_dir():
            print_success(f"{dir_path}/ - {description}")
        else:
            print_warning(f"{dir_path}/ - {description} (MISSING)")
    
    return all_present

def check_configuration():
    """Check if configuration is valid."""
    print_header("Checking Configuration")
    
    try:
        sys.path.append(str(Path('config')))
        from settings import validate_config, OLLAMA_MODEL, EMBEDDING_MODEL_NAME
        
        validate_config()
        print_success("Configuration validation passed")
        print_info(f"LLM Model: {OLLAMA_MODEL}")
        print_info(f"Embedding Model: {EMBEDDING_MODEL_NAME}")
        return True
        
    except ImportError as e:
        print_error(f"Cannot import configuration: {e}")
        return False
    except ValueError as e:
        print_error(f"Configuration validation failed: {e}")
        return False
    except Exception as e:
        print_error(f"Configuration check failed: {e}")
        return False

def main():
    """Run all checks."""
    print(f"{Colors.BOLD}🧪 DoChat+ Installation Test{Colors.END}")
    print("This script will verify your DoChat+ installation.\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("Ollama Setup", check_ollama),
        ("Project Structure", check_project_structure),
        ("Configuration", check_configuration),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print_error(f"Check '{check_name}' failed with exception: {e}")
            results[check_name] = False
    
    # Summary
    print_header("Test Results Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status:<6}{Colors.END} {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print_success("🎉 All checks passed! DoChat+ is ready to run.")
        print_info("Start the application with: python app.py")
    else:
        print_error("❌ Some checks failed. Please address the issues above.")
        print_info("See QUICKSTART.md for setup instructions.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)