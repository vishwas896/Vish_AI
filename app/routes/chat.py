"""
VISH AI - Chat API Route
Handles chat interactions with data collection
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import time
from datetime import datetime

from app.model_handler import get_model_handler
from app.dataset_manager import get_dataset_manager

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    category: str = "assistant"  # assistant, resume, research, business
    history: Optional[List[ChatMessage]] = None
    user_id: Optional[str] = "anonymous"


class ChatResponse(BaseModel):
    response: str
    interaction_id: str
    model_version: str
    response_time: float
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with automatic data collection
    """
    try:
        start_time = time.time()
        
        # Get model handler
        model_handler = get_model_handler()
        
        # Build context from history
        system_prompt = None
        if request.category == "resume":
            system_prompt = "You are an expert resume builder and career advisor. Help users create professional, ATS-friendly resumes."
        elif request.category == "research":
            system_prompt = "You are a knowledgeable research assistant. Provide accurate, well-researched information."
        elif request.category == "business":
            system_prompt = "You are a business consultant. Provide strategic advice for business growth and management."
        
        # Generate response
        ai_response = model_handler.generate_response(
            prompt=request.message,
            max_new_tokens=300,
            temperature=0.7,
            system_prompt=system_prompt
        )
        
        elapsed_time = time.time() - start_time
        
        # Save interaction to dataset
        dataset_mgr = get_dataset_manager()
        interaction_id = dataset_mgr.add_interaction(
            user_prompt=request.message,
            ai_response=ai_response,
            category=request.category,
            metadata={
                "user_id": request.user_id,
                "response_time": elapsed_time,
                "model_version": model_handler.model_version
            }
        )
        
        return ChatResponse(
            response=ai_response,
            interaction_id=interaction_id,
            model_version=model_handler.model_version,
            response_time=round(elapsed_time, 2),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/model-info")
async def get_model_info():
    """Get current model information"""
    model_handler = get_model_handler()
    return model_handler.get_model_info()
