"""
Profile endpoints for user background management.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..db_neon import get_neon_db
from ..models import (
    UserBackgroundRequest, 
    UserBackgroundResponse, 
    UserProfileResponse,
    FullProfileResponse
)
from ..gamification.points import points_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/profile", response_model=dict)
@router.post("/profile", response_model=dict)
async def save_profile(request: UserBackgroundRequest):
    """Save user background for personalization."""
    neon = get_neon_db()
    
    if not neon.enabled:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = await neon.save_user_background(
            user_id=request.user_id,
            software_role=request.software_role,
            software_level=request.software_level,
            hardware_type=request.hardware_type,
            gpu_available=request.gpu_available,
            preferred_language=request.preferred_language
        )
        return {"status": "saved", "id": result}
    except Exception as e:
        logger.error(f"Failed to save profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}", response_model=UserBackgroundResponse)
async def get_profile(user_id: str):
    """Get user background for personalization."""
    neon = get_neon_db()
    
    if not neon.enabled:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        background = await neon.get_user_background(user_id)
        if not background:
            return UserBackgroundResponse(
                user_id=user_id,
                software_role=None,
                software_level=None,
                hardware_type=None,
                gpu_available=False,
                preferred_language="en"
            )
        return UserBackgroundResponse(
            user_id=background["user_id"],
            software_role=background.get("software_role"),
            software_level=background.get("software_level"),
            hardware_type=background.get("hardware_type"),
            gpu_available=background.get("gpu_available", False),
            preferred_language=background.get("preferred_language", "en")
        )
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/full/{user_id}", response_model=FullProfileResponse)
async def get_full_profile(user_id: str):
    """Get full user profile including background and gamification status."""
    neon = get_neon_db()
    
    # 1. Get background
    background_data = await neon.get_user_background(user_id)
    if not background_data:
        background = UserBackgroundResponse(
            user_id=user_id,
            software_role=None,
            software_level=None,
            hardware_type=None,
            gpu_available=False,
            preferred_language="en"
        )
    else:
        background = UserBackgroundResponse(
            user_id=background_data["user_id"],
            software_role=background_data.get("software_role"),
            software_level=background_data.get("software_level"),
            hardware_type=background_data.get("hardware_type"),
            gpu_available=background_data.get("gpu_available", False),
            preferred_language=background_data.get("preferred_language", "en")
        )
    
    # 2. Get status (points/level)
    status = await points_manager.get_user_status(user_id)
    
    return FullProfileResponse(
        background=background,
        status=status
    )
