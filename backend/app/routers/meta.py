"""
Metadata and feedback endpoints for RAG Chatboard.

Provides /meta (collection info) and /feedback (user ratings) endpoints.
"""

import logging
from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, HTTPException

from ..models import MetaResponse, FeedbackRequest, FeedbackResponse
from ..qdrant_client import get_qdrant_service
from ..db_neon import get_neon_db
from ..config import get_settings


# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# API Version
API_VERSION = "1.0.0"


@router.get("/meta", response_model=MetaResponse)
async def get_metadata() -> MetaResponse:
    """
    Get API and collection metadata.
    
    Returns:
    - API version
    - Qdrant collection name and vector count
    - Last ingestion timestamp (if Neon is configured)
    """
    settings = get_settings()
    
    try:
        # Get Qdrant collection info
        qdrant = get_qdrant_service()
        collection_info = await qdrant.get_collection_info()
        
        # Get last ingestion from Neon if available
        last_ingested = None
        neon = get_neon_db()
        if neon.enabled:
            try:
                last_run = await neon.get_last_ingestion()
                if last_run:
                    last_ingested = last_run.get("created_at")
            except Exception as e:
                logger.warning(f"Failed to get last ingestion from Neon: {e}")
        
        return MetaResponse(
            version=API_VERSION,
            collection=collection_info.get("collection", settings.qdrant_collection),
            vectors_count=collection_info.get("vectors_count", 0),
            status=collection_info.get("status", "unknown"),
            last_ingested=last_ingested
        )
        
    except Exception as e:
        logger.error(f"Failed to get metadata: {e}")
        # Return partial info on error
        return MetaResponse(
            version=API_VERSION,
            collection=settings.qdrant_collection,
            vectors_count=0,
            status="error",
            last_ingested=None
        )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """
    Submit user feedback for a chat response.
    
    Stores feedback in Neon if configured, otherwise acknowledges but doesn't persist.
    """
    logger.info(f"Feedback received: session={request.session_id}, rating={request.rating}")
    
    try:
        neon = get_neon_db()
        
        if neon.enabled:
            feedback_id = await neon.save_feedback(
                session_id=request.session_id,
                message_id=request.message_id,
                rating=request.rating,
                comment=request.comment
            )
            
            if feedback_id:
                logger.info(f"Feedback saved with ID: {feedback_id}")
                return FeedbackResponse(
                    status="saved",
                    feedback_id=str(feedback_id)
                )
        
        # Neon not configured - acknowledge but don't persist
        logger.info("Feedback acknowledged (Neon not configured)")
        return FeedbackResponse(
            status="acknowledged",
            feedback_id=None
        )
        
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save feedback: {str(e)}"
        )
