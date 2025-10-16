"""
VISH AI - Retrain API Route
Admin endpoint for triggering model retraining
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import os

from app.retrain import run_training_pipeline
from app.dataset_manager import get_dataset_manager

router = APIRouter()


class RetrainRequest(BaseModel):
    min_samples: int = 10
    epochs: int = 3
    admin_key: str


class RetrainResponse(BaseModel):
    status: str
    message: str
    details: dict


# Simple admin key (in production, use proper auth)
ADMIN_KEY = os.getenv("VISH_ADMIN_KEY", "vish-admin-2024")


@router.post("/retrain", response_model=RetrainResponse)
async def trigger_retrain(request: RetrainRequest):
    """
    Trigger model retraining (admin only)
    
    This will:
    1. Collect all high-quality interactions
    2. Fine-tune Phi-3 with LoRA
    3. Save new model version
    4. Reload the model
    """
    
    # Verify admin key
    if request.admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    try:
        # Get current dataset stats
        dataset_mgr = get_dataset_manager()
        stats = dataset_mgr.get_dataset_stats()
        
        # Run training pipeline
        result = run_training_pipeline(
            min_samples=request.min_samples,
            epochs=request.epochs
        )
        
        if result["status"] == "success":
            message = f"Training completed successfully! New version: {result['version']}"
        elif result["status"] == "skipped":
            message = f"Training skipped: {result['reason']}"
        else:
            message = f"Training failed: {result.get('error', 'Unknown error')}"
        
        return RetrainResponse(
            status=result["status"],
            message=message,
            details={
                **result,
                "dataset_stats": stats
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrain error: {str(e)}")


@router.post("/cleanup")
async def cleanup_dataset(
    admin_key: str,
    min_score: float = 2.0
):
    """
    Remove low-quality data (admin only)
    """
    
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    try:
        dataset_mgr = get_dataset_manager()
        dataset_mgr.clear_low_quality_data(min_score=min_score)
        
        stats = dataset_mgr.get_dataset_stats()
        
        return {
            "status": "success",
            "message": f"Cleaned dataset (removed entries with score < {min_score})",
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup error: {str(e)}")
