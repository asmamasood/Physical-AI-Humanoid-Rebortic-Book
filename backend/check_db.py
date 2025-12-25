import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load env variables from parent directory
load_dotenv("../.env")

DB_URL = os.getenv("NEON_DB_URL")

async def check_db():
    if not DB_URL:
        print("Error: NEON_DB_URL is not set in .env")
        return

    print(f"Connecting to Database: {DB_URL.split('@')[1] if '@' in DB_URL else '...'}")
    
    try:
        conn = await asyncpg.connect(DB_URL)
        
        # 1. List Tables
        print("\n--- TABLES ---")
        rows = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        for row in rows:
            print(f"- {row['table_name']}")

        # 2. Check Users (Better Auth)
        print("\n--- USERS (Better Auth) ---")
        try:
            users = await conn.fetch("SELECT id, name, email FROM \"user\"")
            if not users:
                print("No users found.")
            for u in users:
                print(f"ID: {u['id']}, Name: {u['name']}, Email: {u['email']}")
        except Exception as e:
            print(f"Error querying users: {e}")

        # 3. Check Chat History
        print("\n--- CHAT HISTORY ---")
        try:
            chats = await conn.fetch("SELECT id, user_id, created_at, SUBSTRING(messages::text, 1, 100) as preview FROM conversations ORDER BY created_at DESC LIMIT 5")
            if not chats:
                print("No conversations found.")
            for c in chats:
                print(f"ID: {c['id']}, User: {c['user_id']}, Time: {c['created_at']}")
                print(f"  Preview: {c['preview']}...")
        except Exception as e:
            print(f"Error querying conversations: {e}")

        await conn.close()
        
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
