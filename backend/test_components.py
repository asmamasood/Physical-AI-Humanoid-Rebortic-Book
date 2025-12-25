import asyncio
import os
import logging
from dotenv import load_dotenv
from app.config import get_settings
from app.local_embedder import get_local_embedder
from app.qdrant_client import get_qdrant_service
from app.gemini_agent import get_gemini_agent

# Configure logging to show everything
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_all():
    load_dotenv()
    settings = get_settings()
    logger.info(f"Using Collection: {settings.qdrant_collection}")
    logger.info(f"Embedding Provider: {settings.embedding_provider}")

    # 1. Test Embedding
    logger.info("Testing Embedding...")
    embedder = get_local_embedder()
    query = "Summarize this page 📖"
    embedding = await embedder.embed_query(query)
    logger.info(f"Got embedding of size {len(embedding)}")

    # 2. Test Qdrant Search
    logger.info("Testing Qdrant Search...")
    qdrant = get_qdrant_service()
    # Corrected filter: using title as stored in payload
    module_id = "module-1"
    chapter_id = "Chapter 1: Introduction to ROS 2"
    
    try:
        chunks = await qdrant.search_chunks(
            query_embedding=embedding,
            top_k=5,
            filter_module=module_id,
            filter_chapter=chapter_id
        )
        logger.info(f"Retrieved {len(chunks)} chunks")
        for i, c in enumerate(chunks):
            logger.info(f"Chunk {i}: {c.get('chapter')} - {c.get('content')[:50]}...")
    except Exception as e:
        import traceback
        with open("error_trace.txt", "w") as f:
            f.write(traceback.format_exc())
        logger.error(f"Qdrant Search Failed: {e}. Traceback saved to error_trace.txt")
        return

    # 3. Test Gemini
    logger.info("Testing Gemini...")
    agent = get_gemini_agent()
    try:
        answer, citations = await agent.generate_rag_answer(
            query=query,
            chunks=chunks,
            history=[],
            user_profile=None
        )
        logger.info(f"Gemini Answer: {answer[:100]}...")
        logger.info(f"Citations: {len(citations)}")
    except Exception as e:
        logger.error(f"Gemini Failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_all())
