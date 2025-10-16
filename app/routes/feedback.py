"""
VISH AI - Feedback API Route
Handles user feedback collection for continuous improvement
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.dataset_manager import get_dataset_manager

router = APIRouter()


class FeedbackRequest(BaseModel):
    interaction_id: str
    score: int = Field(..., ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    message: str


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for a chat interaction
    This data is used to filter training data quality
    """
    try:
        dataset_mgr = get_dataset_manager()
        
        dataset_mgr.add_feedback(
            interaction_id=request.interaction_id,
            score=request.score,
            comment=request.comment
        )
        
        return FeedbackResponse(
            status="success",
            message=f"Feedback recorded for interaction {request.interaction_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback error: {str(e)}")


@router.get("/stats")
async def get_dataset_stats():
    """Get dataset statistics"""
    dataset_mgr = get_dataset_manager()
    stats = dataset_mgr.get_dataset_stats()
    return stats
