"""
Chat endpoints for RAG Chatboard.

Provides /chat (RAG-based) and /selective-chat (selection-only) endpoints.
"""

import logging
import uuid
import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..models import (
    ChatRequest,
    SelectiveChatRequest,
    ChatResponse,
    Citation,
)
from ..cohere_client import get_cohere_embedder
from ..local_embedder import get_local_embedder
from ..qdrant_client import get_qdrant_service
from ..gemini_agent import get_gemini_agent
from ..db_neon import get_neon_db
from ..config import get_settings
from ..gamification.points import points_manager


# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    RAG-based chat endpoint.
    
    1. Embeds the query (Local or Cohere)
    2. Searches Qdrant for relevant chunks
    3. Passes chunks to Gemini for answer synthesis
    4. Returns answer with citations
    """
    settings = get_settings()
    logger.info(f"Chat request: query='{request.query[:50]}...', top_k={request.top_k}")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Step 1: Embed query
        if settings.embedding_provider == "local":
            embedder = get_local_embedder()
        else:
            embedder = get_cohere_embedder()
            
        query_embedding = await embedder.embed_query(request.query)
        
        # Step 2: Search Qdrant
        qdrant = get_qdrant_service()
        chunks = await qdrant.search_chunks(
            query_embedding=query_embedding,
            top_k=request.top_k,
            filter_module=request.module_id,
            filter_chapter=request.chapter_id
        )
        
        logger.info(f"Retrieved {len(chunks)} chunks from Qdrant (Filter: mod={request.module_id}, ch={request.chapter_id})")
        
        # Step 3: Generate answer
        neon = get_neon_db()
        history = []
        user_profile = None
        subagent = None
        gamification_status = None

        if neon.enabled and request.user_id:
            try:
                # Parallel fetch history, background, and points
                history_task = neon.get_chat_history(
                    user_id=request.user_id,
                    session_id=session_id,
                    limit=5
                )
                background_task = neon.get_user_background(request.user_id)
                points_task = points_manager.get_user_status(request.user_id)
                agent_task = neon.get_subagent_full(request.agent_id) if request.agent_id else None

                results = await asyncio.gather(
                    history_task,
                    background_task,
                    points_task,
                    agent_task if agent_task else asyncio.sleep(0, result=None)
                )

                history, user_profile, gamification_status, subagent = results[0], results[1], results[2], results[3]
            except Exception as e:
                logger.warning(f"Failed to fetch user data from Neon: {e}")
                gamification_status = None

        agent = get_gemini_agent()
        answer, citations = await agent.generate_rag_answer(
            query=request.query,
            chunks=chunks,
            history=history,
            user_profile=user_profile,
            gamification_status=gamification_status,
            subagent=subagent,
            selected_text=request.selected_text
        )
        
        # Step 4: Save to New ChatKit History
        if neon.enabled and request.user_id: # Only save if we have a user_id
            try:
                # Use session_id as thread_id for now, or generate new UUID if needed
                thread_id = session_id 
                
                # Check if it's a valid UUID, if not generate one (fallback)
                try: 
                    uuid.UUID(thread_id)
                except ValueError:
                    thread_id = str(uuid.uuid4())

                await neon.save_chat_interaction(
                    thread_id=thread_id,
                    user_id=request.user_id,
                    user_message=request.query,
                    assistant_message=answer
                )
            except Exception as e:
                logger.warning(f"Failed to save to ChatKit history: {e}")

        # Legacy save (optional, keep for backward compatibility if needed)
        if neon.enabled:
            try:
                citations_dict = [c.model_dump() for c in citations]
                await neon.save_conversation(
                    session_id=session_id,
                    query=request.query,
                    response=answer,
                    citations=citations_dict,
                    user_id=request.user_id
                )
            except Exception as e:
                logger.warning(f"Failed to save to legacy conversation table: {e}")
        
        logger.info(f"Generated answer with {len(citations)} citations")
        
        return ChatResponse(
            answer=answer,
            citations=citations,
            session_id=session_id
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Chat error: {e}\n{error_trace}")
        
        # Determine if it's a rate limit error
        error_msg = str(e)
        if "429" in error_msg or "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
            friendly_msg = "Gemini API Quota Exceeded. Please wait a minute and try again."
        else:
            friendly_msg = f"Failed to process chat request: {error_msg}"
            
        raise HTTPException(
            status_code=500,
            detail=friendly_msg
        )


@router.post("/selective-chat", response_model=ChatResponse)
async def selective_chat(request: SelectiveChatRequest) -> ChatResponse:
    """
    Selective chat endpoint - answers from selection text ONLY.
    
    CRITICAL: This endpoint does NOT query Qdrant.
    It passes only the user's selection_text to Gemini.
    
    If the answer is not found in the selection, returns appropriate message.
    """
    logger.info(f"Selective chat: query='{request.query[:50]}...', selection_length={len(request.selection_text)}")
    
    # CRITICAL: Log that we are NOT using Qdrant
    logger.info("SELECTIVE MODE: Qdrant lookup SKIPPED - using only selection_text")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Generate answer from selection ONLY
        # CRITICAL: No Qdrant call here
        agent = get_gemini_agent()
        answer = await agent.generate_selective_answer(
            query=request.query,
            selection_text=request.selection_text
        )
        
        # Check for NOT_FOUND response
        if answer.strip().upper() == "NOT_FOUND" or "NOT_FOUND" in answer.upper():
            return ChatResponse(
                answer="Answer not found in selected text.",
                citations=[],
                session_id=session_id
            )
        
        # Create citation for the selection
        citations = []
        if request.selection_meta:
            citations.append(Citation(
                module="selection",
                chapter="user_selection",
                chunk_id="selection",
                source_url=request.selection_meta.get("url", ""),
                score=None
            ))
        
        # Save to Neon
        neon = get_neon_db()
        if neon.enabled:
            # Save to new ChatKit history if user_id is provided
            if request.user_id:
                try:
                    thread_id = session_id
                    try:
                        uuid.UUID(thread_id)
                    except ValueError:
                        thread_id = str(uuid.uuid4())

                    await neon.save_chat_interaction(
                        thread_id=thread_id,
                        user_id=request.user_id,
                        user_message=f"[Selection] {request.query}",
                        assistant_message=answer
                    )
                except Exception as e:
                    logger.warning(f"Failed to save to ChatKit history (selective): {e}")

            # Legacy save
            try:
                citations_dict = [c.model_dump() for c in citations]
                await neon.save_conversation(
                    session_id=session_id,
                    query=request.query,
                    response=answer,
                    citations=citations_dict,
                    user_id=request.user_id
                )
            except Exception as e:
                logger.warning(f"Failed to save conversation to Neon: {e}")
        
        logger.info("Selective chat completed successfully")
        
        return ChatResponse(
            answer=answer,
            citations=citations,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Selective chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process selective chat request: {str(e)}"
        )
