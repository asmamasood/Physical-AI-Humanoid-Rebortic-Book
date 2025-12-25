"""
Personalization endpoints for chapter content adaptation.
"""

import logging
import asyncio
import hashlib
from typing import Optional, Dict
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from google import genai

from ..config import get_settings
from ..db_neon import get_neon_db
from ..middleware.auth import require_user_id


logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory cache: {cache_key: (content, timestamp)}
_personalization_cache: Dict[str, tuple] = {}
CACHE_TTL_MINUTES = 60


class PersonalizeRequest(BaseModel):
    """Request body for content personalization."""
    user_id: str = Field(..., min_length=1, description="User ID for fetching background")
    chapter_title: str = Field(..., min_length=1, max_length=200, description="Title of the chapter")
    chapter_content: str = Field(..., min_length=50, max_length=50000, description="Original chapter content")

    @field_validator('user_id', 'chapter_title')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class PersonalizeResponse(BaseModel):
    """Response body for personalized content."""
    personalized_content: str
    personalization_applied: bool
    user_profile_summary: Optional[str]
    cached: bool = False


def _get_cache_key(user_id: str, chapter_title: str) -> str:
    """Generate cache key from user_id and chapter_title."""
    return hashlib.md5(f"{user_id}:{chapter_title}".encode()).hexdigest()


def _get_cached(cache_key: str) -> Optional[str]:
    """Get cached personalization if not expired."""
    if cache_key in _personalization_cache:
        content, timestamp = _personalization_cache[cache_key]
        if datetime.now() - timestamp < timedelta(minutes=CACHE_TTL_MINUTES):
            return content
        else:
            del _personalization_cache[cache_key]
    return None


def _set_cache(cache_key: str, content: str):
    """Cache personalized content."""
    _personalization_cache[cache_key] = (content, datetime.now())


PERSONALIZATION_PROMPT = """You are an expert educator. Adapt the following chapter content for a specific learner.

LEARNER PROFILE:
- Software Background: {software_role} ({software_level} level)
- Hardware Setup: {hardware_type}
- GPU Available: {gpu_available}

INSTRUCTIONS:
1. Adjust technical depth based on the learner's experience level
2. Use examples relevant to their software background
3. If they have limited hardware, suggest alternatives or cloud-based solutions
4. Keep the same structure but make it more accessible for this specific learner
5. If GPU is not available, emphasize CPU-based alternatives

ORIGINAL CHAPTER: {chapter_title}

CONTENT:
{chapter_content}

PERSONALIZED VERSION:"""


@router.post("/personalize", response_model=PersonalizeResponse)
async def personalize_chapter(request: PersonalizeRequest):
    """Personalize chapter content based on user background."""
    neon = get_neon_db()
    settings = get_settings()
    
    # Check cache first
    cache_key = _get_cache_key(request.user_id, request.chapter_title)
    cached_content = _get_cached(cache_key)
    if cached_content:
        logger.info(f"Cache hit for user {request.user_id}, chapter: {request.chapter_title}")
        return PersonalizeResponse(
            personalized_content=cached_content,
            personalization_applied=True,
            user_profile_summary="From cache",
            cached=True
        )
    
    # Get user background
    background = None
    if neon.enabled:
        try:
            background = await neon.get_user_background(request.user_id)
        except Exception as e:
            logger.warning(f"Failed to fetch user background: {e}")
    
    # Fallback if no profile
    if not background:
        return PersonalizeResponse(
            personalized_content=request.chapter_content,
            personalization_applied=False,
            user_profile_summary="No profile found. Showing default content."
        )
    
    # Build personalization prompt
    prompt = PERSONALIZATION_PROMPT.format(
        software_role=background.get("software_role", "General"),
        software_level=background.get("software_level", "Intermediate"),
        hardware_type=background.get("hardware_type", "Mid-range PC"),
        gpu_available="Yes" if background.get("gpu_available") else "No",
        chapter_title=request.chapter_title,
        chapter_content=request.chapter_content
    )
    
    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=settings.gemini_model_name,
                contents=prompt
            )
        )
        
        personalized = response.text.strip()
        
        # Cache the result
        _set_cache(cache_key, personalized)
        
        profile_summary = f"{background.get('software_role', 'N/A')} ({background.get('software_level', 'N/A')}) on {background.get('hardware_type', 'N/A')}"
        
        return PersonalizeResponse(
            personalized_content=personalized,
            personalization_applied=True,
            user_profile_summary=profile_summary
        )
    except Exception as e:
        logger.error(f"Personalization failed: {e}")
        return PersonalizeResponse(
            personalized_content=request.chapter_content,
            personalization_applied=False,
            user_profile_summary=f"Personalization failed: {str(e)}"
        )
