"""
VISH AI - Main Application
FastAPI + Gradio combined server with self-training capabilities
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr
import uvicorn
from contextlib import asynccontextmanager

# Import routes
from app.routes import chat, feedback, retrain
from app.model_handler import get_model_handler
from app.dataset_manager import get_dataset_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize model on startup"""
    print("=" * 60)
    print("🚀 Initializing VISH AI Self-Training System")
    print("=" * 60)
    
    # Load model
    model_handler = get_model_handler()
    print(f"✅ Model loaded: {model_handler.model_version}")
    
    # Initialize dataset manager
    dataset_mgr = get_dataset_manager()
    stats = dataset_mgr.get_dataset_stats()
    print(f"📊 Dataset: {stats['total_interactions']} interactions")
    print(f"⭐ Feedback: {stats['total_feedback']} ratings (avg: {stats['avg_feedback_score']})")
    
    print("=" * 60)
    yield
    print("Shutting down VISH AI...")


# Create FastAPI app
app = FastAPI(
    title="VISH AI API",
    description="Self-improving AI assistant with continuous learning",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(retrain.router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "VISH AI",
        "version": "1.0.0",
        "features": [
            "Chat Assistant",
            "Resume Builder",
            "Research Assistant",
            "Self-Training",
            "Continuous Learning"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    model_handler = get_model_handler()
    dataset_mgr = get_dataset_manager()
    
    return {
        "status": "healthy",
        "model": model_handler.get_model_info(),
        "dataset": dataset_mgr.get_dataset_stats()
    }


# Mount Gradio interface
from app.gradio_ui import create_gradio_interface

gradio_app = create_gradio_interface()
app = gr.mount_gradio_app(app, gradio_app, path="/")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7860,
        reload=False
    )
