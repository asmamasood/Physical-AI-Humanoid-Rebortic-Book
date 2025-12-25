from typing import List
from fastapi import APIRouter, HTTPException, Depends
from ..db_neon import get_neon_db
from ..models import ChatThread, ChatMessage, ChatHistoryResponse

router = APIRouter()

@router.get("/history", response_model=ChatHistoryResponse)
async def get_history(user_id: str):
    """List all chat threads for a user."""
    db = get_neon_db()
    
    # Check if DB is enabled
    if not db.enabled:
        return {"threads": []}
    
    await db.connect()
    async with db.pool.acquire() as conn:
        try:
            rows = await conn.fetch("""
                SELECT id, user_id, title, created_at 
                FROM chat_threads 
                WHERE user_id = $1 
                ORDER BY created_at DESC
            """, user_id)
            
            # specific conversion for UUID to str for Pydantic
            threads = []
            for r in rows:
                data = dict(r)
                data['id'] = str(data['id'])
                threads.append(ChatThread(**data))
            
            return {"threads": threads}
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")

@router.get("/history/{thread_id}/messages", response_model=List[ChatMessage])
async def get_thread_messages(thread_id: str, user_id: str):
    """Get all messages for a specific thread."""
    db = get_neon_db()
    
    if not db.enabled:
        return []

    await db.connect()
    async with db.pool.acquire() as conn:
        # Verify ownership first
        thread = await conn.fetchrow("SELECT 1 FROM chat_threads WHERE id = $1 AND user_id = $2", thread_id, user_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        rows = await conn.fetch("""
            SELECT id, thread_id, role, content, created_at 
            FROM chat_messages 
            WHERE thread_id = $1 
            ORDER BY created_at ASC
        """, thread_id)
        
        return [ChatMessage(**dict(r)) for r in rows]

@router.delete("/history/{thread_id}")
async def delete_thread(thread_id: str, user_id: str):
    """Delete a thread and its messages."""
    db = get_neon_db()
    
    if not db.enabled:
        raise HTTPException(status_code=503, detail="Database not enabled")

    await db.connect()
    async with db.pool.acquire() as conn:
        result = await conn.execute("DELETE FROM chat_threads WHERE id = $1 AND user_id = $2", thread_id, user_id)
        
        if result == "DELETE 0":
             raise HTTPException(status_code=404, detail="Thread not found")
            
    return {"status": "deleted", "id": thread_id}
