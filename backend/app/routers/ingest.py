"""
Ingestion endpoint for RAG Chatboard.

Provides admin-protected endpoint to trigger content ingestion.
"""

import logging
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ..models import IngestRequest, IngestResponse
from ..middleware.auth import verify_admin
from ..db_neon import get_neon_db


# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/ingest",
    response_model=IngestResponse,
    dependencies=[Depends(verify_admin)]
)
async def trigger_ingestion(request: IngestRequest = None) -> IngestResponse:
    """
    Trigger content ingestion pipeline.
    
    This endpoint is protected by admin authentication.
    
    1. Collects chapters from docs directory
    2. Chunks content
    3. Embeds via Cohere
    4. Upserts to Qdrant
    """
    logger.info("Ingestion triggered via API")
    
    try:
        # Add scripts directory to path for imports
        backend_dir = Path(__file__).parent.parent.parent
        project_root = backend_dir.parent
        scripts_dir = project_root / "scripts"
        
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        
        # Import ingestion functions
        from scripts.run_ingestion import run_ingestion
        
        # Determine docs path
        docs_path = None
        if request and request.repo_path_or_url:
            docs_path = Path(request.repo_path_or_url)
        
        # Run ingestion
        result = run_ingestion(docs_path=docs_path)
        
        # Save to Neon if available
        neon = get_neon_db()
        if neon.enabled:
            try:
                await neon.save_ingestion_run(
                    files_processed=result.files_processed,
                    chunks_created=result.chunks_created,
                    vectors_upserted=result.vectors_upserted,
                    duration_seconds=result.duration_seconds,
                    errors=result.errors
                )
            except Exception as e:
                logger.warning(f"Failed to save ingestion run to Neon: {e}")
        
        status = "completed" if not result.errors else "completed_with_errors"
        
        logger.info(f"Ingestion {status}: {result.vectors_upserted} vectors")
        
        return IngestResponse(
            status=status,
            files_processed=result.files_processed,
            chunks_created=result.chunks_created,
            vectors_upserted=result.vectors_upserted,
            duration_seconds=result.duration_seconds,
            errors=result.errors
        )
        
    except ImportError as e:
        logger.error(f"Failed to import ingestion scripts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion scripts not available: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}"
        )
