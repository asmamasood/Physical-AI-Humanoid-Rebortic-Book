import asyncio
from backend.app.db_neon import get_neon_db
from backend.app.config import get_settings

async def test_db():
    print("Testing Neon DB Connection...")
    settings = get_settings()
    print(f"DB URL Set: {'Yes' if settings.neon_db_url else 'No'}")
    
    db = get_neon_db()
    if not db.enabled:
        print("DB is disabled in settings.")
        return
        
    try:
        await db.connect()
        print("Successfully connected to Neon DB!")
        
        # Test a simple query
        async with db.pool.acquire() as conn:
            val = await conn.fetchval("SELECT 1")
            print(f"Query Result: {val}")
            
        await db.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_db())
