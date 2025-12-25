"""
Translation endpoints for Urdu support.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..gemini_agent import get_gemini_agent

logger = logging.getLogger(__name__)
router = APIRouter()

class TranslateRequest(BaseModel):
    """Request body for translation."""
    text: str = Field(..., min_length=1, description="Text to translate")

class TranslateResponse(BaseModel):
    """Response body for translated content."""
    translated_text: str

@router.post("/translate", response_model=TranslateResponse)
async def translate_to_urdu(request: TranslateRequest):
    """Translate English text to Urdu using Gemini."""
    try:
        agent = get_gemini_agent()
        urdu_text = await agent.translate_to_urdu(request.text)
        
        return TranslateResponse(translated_text=urdu_text)
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
