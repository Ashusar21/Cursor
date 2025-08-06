import os
import sys
import base64
import subprocess
import tempfile
import numpy as np
import logging
from typing import List, Optional, Tuple
from pathlib import Path
from pypdf import PdfReader

import gradio as gr
import faiss
from sentence_transformers import SentenceTransformer

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_core.documents import Document

# Add config directory to path
sys.path.append(str(Path(__file__).parent / "config"))

# Import configuration
try:
    from settings import *
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    logger.info(f"Loaded configuration: {APP_NAME} v{APP_VERSION}")
except ImportError as e:
    # Fallback configuration if config file is not available
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not load config file: {e}. Using fallback configuration.")
    
    # Fallback values
    OLLAMA_MODEL = "llama3.1:8b-instruct-q5_K_M"
    EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 200
    CHUNK_SEPARATORS = ["\n\n", "\n", " ", ""]
    RETRIEVAL_K = 4
    RETRIEVAL_FETCH_K = 8
    MMR_LAMBDA = 0.5
    CHAIN_TYPE = "stuff"
    RETURN_SOURCE_DOCS = True
    OLLAMA_TEMPERATURE = 0.2
    OLLAMA_TIMEOUT = 60
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 7860
    ENABLE_QUEUE = True

# Initialize embedding model
try:
    EMBED_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    raise

# ---------------------
# 2) GLOBAL STATE
# ---------------------
DOCUMENT_PAGES: List[str] = []
CURRENT_PAGE: int = 0
QA_CHAIN: Optional[RetrievalQA] = None
RETRIEVER = None
VECTOR_STORE = None

# ---------------------
# 3) UTILITIES
# ---------------------
def extract_pages(path: str) -> List[str]:
    """Extract text from all pages of a PDF."""
    try:
        reader = PdfReader(path)
        pages = [p.extract_text() or "" for p in reader.pages]
        logger.info(f"Extracted {len(pages)} pages from PDF")
        return pages
    except Exception as e:
        logger.error(f"Error extracting pages: {e}")
        raise

def build_rag(pdf_path: str) -> None:
    """Build RAG pipeline with FAISS vector store."""
    global DOCUMENT_PAGES, CURRENT_PAGE, QA_CHAIN, RETRIEVER, VECTOR_STORE

    try:
        logger.info("Starting RAG pipeline construction...")
        
        # 1) Extract raw pages
        DOCUMENT_PAGES = extract_pages(pdf_path)
        CURRENT_PAGE = 0

        # 2) Load and chunk documents
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP,
            separators=CHUNK_SEPARATORS
        )
        chunks = splitter.split_documents(docs)
        logger.info(f"Created {len(chunks)} text chunks")

        # 3) Create embeddings and FAISS vector store
        embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={'device': EMBEDDING_DEVICE},
            encode_kwargs={'normalize_embeddings': NORMALIZE_EMBEDDINGS}
        )
        
        # Create FAISS vector store
        VECTOR_STORE = FAISS.from_documents(
            documents=chunks,
            embedding=embedding_model
        )
        logger.info("Created FAISS vector store")

        # 4) Create retriever with MMR
        RETRIEVER = VECTOR_STORE.as_retriever(
            search_type="mmr",
            search_kwargs={"k": RETRIEVAL_K, "fetch_k": RETRIEVAL_FETCH_K, "lambda_mult": MMR_LAMBDA}
        )

        # 5) Initialize LLM and QA chain
        llm = Ollama(
            model=OLLAMA_MODEL,
            temperature=OLLAMA_TEMPERATURE,
            timeout=OLLAMA_TIMEOUT
        )
        
        QA_CHAIN = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type=CHAIN_TYPE,
            retriever=RETRIEVER,
            return_source_documents=RETURN_SOURCE_DOCS,
            verbose=VERBOSE_CHAIN
        )
        
        logger.info("RAG pipeline construction completed successfully")
        
    except Exception as e:
        logger.error(f"Error building RAG pipeline: {e}")
        raise

# ---------------------
# 4) HANDLERS
# ---------------------
def upload_and_process(pdf_file) -> Tuple[str, str, str]:
    """Handle PDF upload and processing."""
    if pdf_file is None:
        return "❌ No file uploaded", "", ""
    
    try:
        logger.info(f"Processing uploaded file: {pdf_file.name}")
        
        # Build RAG index
        build_rag(pdf_file.name)
        
        # Create preview snippet
        snippet = ""
        if DOCUMENT_PAGES:
            first_page = DOCUMENT_PAGES[0]
            snippet = first_page[:500] + "…" if len(first_page) > 500 else first_page
        
        # Create PDF preview embed
        with open(pdf_file.name, "rb") as f:
            raw = f.read()
        b64 = base64.b64encode(raw).decode()
        embed = (
            f'<object data="data:application/pdf;base64,{b64}" '
            'type="application/pdf" width="100%" height="600px">'
            "PDF preview not available</object>"
        )
        
        return "✅ PDF loaded and RAG pipeline built successfully", embed, snippet
        
    except Exception as e:
        error_msg = f"❌ Error processing PDF: {str(e)}"
        logger.error(error_msg)
        return error_msg, "", ""

def show_prev_page() -> str:
    """Navigate to previous page."""
    global CURRENT_PAGE
    
    if not DOCUMENT_PAGES:
        return "No pages loaded"
    
    CURRENT_PAGE = max(0, CURRENT_PAGE - 1)
    txt = DOCUMENT_PAGES[CURRENT_PAGE]
    return f"Page {CURRENT_PAGE + 1}/{len(DOCUMENT_PAGES)}\n\n" + (txt[:500] + "…" if len(txt) > 500 else txt)

def show_next_page() -> str:
    """Navigate to next page."""
    global CURRENT_PAGE
    
    if not DOCUMENT_PAGES:
        return "No pages loaded"
    
    CURRENT_PAGE = min(len(DOCUMENT_PAGES) - 1, CURRENT_PAGE + 1)
    txt = DOCUMENT_PAGES[CURRENT_PAGE]
    return f"Page {CURRENT_PAGE + 1}/{len(DOCUMENT_PAGES)}\n\n" + (txt[:500] + "…" if len(txt) > 500 else txt)

def chat_and_retrieve(mode: str, query: str, history: List) -> Tuple[List, List, str]:
    """Handle chat queries and document retrieval."""
    if QA_CHAIN is None:
        return history, history, "❌ Please upload a PDF first"

    history = history or []
    
    if not query.strip() and mode != "Summarize":
        return history, history, "❌ Please enter a question"

    try:
        if mode == "Summarize":
            logger.info("Generating document summary...")
            
            # Create a comprehensive summary using chunks
            if RETRIEVER:
                # Get representative chunks
                sample_docs = RETRIEVER.get_relevant_documents("summary main points key information")
                context = "\n\n".join([doc.page_content for doc in sample_docs[:6]])
            else:
                # Fallback to first few pages
                context = "\n\n".join(DOCUMENT_PAGES[:3])
            
            llm = Ollama(model=OLLAMA_MODEL, temperature=OLLAMA_TEMPERATURE)
            prompt = f"""Please provide a comprehensive summary of this document in 3-4 sentences, highlighting the main points and key information:

{context}

Summary:"""
            
            summary = llm.invoke(prompt)
            history.append(("[Document Summary]", summary.strip()))
            return history, history, "Summary generated from document content"

        # Ask mode - Q&A
        logger.info(f"Processing query: {query}")
        
        # Get relevant documents
        docs = RETRIEVER.get_relevant_documents(query)
        retrieved_text = "\n\n---\n\n".join([doc.page_content for doc in docs])
        
        # Generate answer
        result = QA_CHAIN.invoke({"query": query})
        answer = result["result"].strip()
        
        history.append((query, answer))
        return history, history, retrieved_text
        
    except Exception as e:
        error_msg = f"❌ Error processing request: {str(e)}"
        logger.error(error_msg)
        history.append((query if mode == "Ask" else "[Summary]", error_msg))
        return history, history, ""

def export_history(history: List) -> Optional[str]:
    """Export chat history to a text file."""
    if not history:
        return None
    
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure exports directory exists
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        filename = exports_dir / f"dochat_export_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("DoChat+ - Chat Export\n")
            f.write("=" * 50 + "\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Conversations: {len(history)}\n")
            f.write("=" * 50 + "\n\n")
            
            for i, (question, answer) in enumerate(history, 1):
                f.write(f"Entry {i}:\n")
                f.write(f"Q: {question}\n")
                f.write(f"A: {answer}\n")
                f.write("-" * 30 + "\n\n")
        
        logger.info(f"Exported chat history to {filename}")
        return str(filename)
        
    except Exception as e:
        logger.error(f"Error exporting history: {e}")
        return None

# ---------------------
# 5) GRADIO UI
# ---------------------
def create_interface():
    """Create and configure the Gradio interface."""
    
    with gr.Blocks(
        title="DoChat+ - Offline AI Document Intelligence",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .chat-message {
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 📄 DoChat+ — Offline AI-Powered Document Intelligence
        
        **Privacy-preserving PDF Q&A powered by LLaMA 3.1 8B + RAG**
        
        Upload a PDF, ask questions, get summaries - all processed locally without internet connectivity.
        """)
        
        # File upload section
        with gr.Row():
            with gr.Column(scale=2):
                pdf_input = gr.File(
                    label="📁 Upload PDF Document", 
                    file_types=[".pdf"],
                    height=100
                )
            with gr.Column(scale=1):
                upload_btn = gr.Button("🚀 Process PDF", variant="primary", size="lg")
        
        status_output = gr.Textbox(label="📊 Status", interactive=False)
        
        # PDF preview and navigation
        with gr.Row():
            with gr.Column(scale=2):
                preview_pdf = gr.HTML(label="📄 PDF Preview")
            with gr.Column(scale=1):
                preview_text = gr.Textbox(
                    label="📖 Page Content Preview", 
                    lines=10,
                    max_lines=15
                )
                
                with gr.Row():
                    prev_btn = gr.Button("⬅️ Previous", size="sm")
                    next_btn = gr.Button("➡️ Next", size="sm")
        
        # Chat interface
        gr.Markdown("## 💬 Chat Interface")
        
        chatbot = gr.Chatbot(
            label="Chat History",
            height=400,
            show_label=True,
            container=True
        )
        
        with gr.Row():
            with gr.Column(scale=3):
                question_input = gr.Textbox(
                    placeholder="Ask a question about your document...",
                    label="Your Question",
                    lines=2
                )
            with gr.Column(scale=1):
                mode_radio = gr.Radio(
                    choices=["Ask", "Summarize"],
                    value="Ask",
                    label="Mode"
                )
                send_btn = gr.Button("📤 Send", variant="primary")
        
        # Retrieved context display
        retrieved_context = gr.Textbox(
            label="🔍 Retrieved Context",
            lines=6,
            max_lines=10,
            placeholder="Relevant document passages will appear here..."
        )
        
        # Export functionality
        with gr.Row():
            export_btn = gr.Button("💾 Export Chat History", variant="secondary")
            download_file = gr.File(label="📥 Download", visible=False)
        
        # Event handlers
        upload_btn.click(
            fn=upload_and_process,
            inputs=[pdf_input],
            outputs=[status_output, preview_pdf, preview_text]
        )
        
        prev_btn.click(
            fn=show_prev_page,
            inputs=[],
            outputs=[preview_text]
        )
        
        next_btn.click(
            fn=show_next_page,
            inputs=[],
            outputs=[preview_text]
        )
        
        send_btn.click(
            fn=chat_and_retrieve,
            inputs=[mode_radio, question_input, chatbot],
            outputs=[chatbot, chatbot, retrieved_context]
        ).then(
            lambda: "",  # Clear input after sending
            outputs=[question_input]
        )
        
        # Allow Enter key to send message
        question_input.submit(
            fn=chat_and_retrieve,
            inputs=[mode_radio, question_input, chatbot],
            outputs=[chatbot, chatbot, retrieved_context]
        ).then(
            lambda: "",
            outputs=[question_input]
        )
        
        export_btn.click(
            fn=export_history,
            inputs=[chatbot],
            outputs=[download_file]
        ).then(
            lambda x: gr.update(visible=bool(x)),
            inputs=[download_file],
            outputs=[download_file]
        )
    
    return demo

# ---------------------
# 6) MAIN
# ---------------------
if __name__ == "__main__":
    try:
        logger.info("Starting DoChat+ application...")
        
        # Check if Ollama is running
        try:
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                logger.info("Ollama is running and accessible")
                if OLLAMA_MODEL.split(':')[0] not in result.stdout:
                    logger.warning(f"Model {OLLAMA_MODEL} not found. Please run: ollama pull {OLLAMA_MODEL}")
            else:
                logger.warning("Ollama might not be running. Please start Ollama service.")
        except subprocess.TimeoutExpired:
            logger.warning("Ollama check timed out")
        except FileNotFoundError:
            logger.error("Ollama not found. Please install Ollama first.")
        
        # Create and launch the interface
        demo = create_interface()
        demo.launch(
            server_name=SERVER_HOST,
            server_port=SERVER_PORT,
            share=SHARE_GRADIO,
            show_error=True,
            enable_queue=ENABLE_QUEUE
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
