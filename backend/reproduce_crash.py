import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

print("Starting reproduction script...")

try:
    print("Importing gemini_agent...")
    from app.gemini_agent import GeminiAgent
    print("GeminiAgent imported.")

    print("Instantiating GeminiAgent...")
    agent = GeminiAgent()
    print("GeminiAgent instantiated successfully.")

    print("Testing simple generation...")
    import asyncio
    
    async def main():
        try:
            # 1. Test Generation
            print("1. Testing Generation...")
            response = await agent.model.generate_content_async("Hello")
            print(f"   Generation success: {response.text}")
            
            # 2. Test Local Embedder
            print("2. Testing Local Embedder...")
            from app.local_embedder import get_local_embedder
            embedder = get_local_embedder()
            emb = await embedder.embed_query("test")
            print(f"   Embedder success. Vector len: {len(emb)}")
            
            # 3. Test Qdrant
            print("3. Testing Qdrant Service...")
            from app.qdrant_client import get_qdrant_service
            qdrant = get_qdrant_service()
            
            # Get info (sync call wrapped or direct)
            # In qdrant_client.py, get_collection_info is async. Let's use that.
            print("   Checking collection info...")
            info = await qdrant.get_collection_info()
            print(f"   Collection info: {info}")
            
            print("   Testing search...")
            search_res = await qdrant.search_chunks(emb, top_k=1)
            print(f"   Qdrant search success. Results: {len(search_res)}")
            
            # 4. Test Neon DB
            print("4. Testing Neon DB...")
            from app.db_neon import get_neon_db
            neon = get_neon_db()
            if neon.enabled:
                print("   Neon enabled. Connecting...")
                await neon.connect()
                print("   Neon connection successful.")
                await neon.close()
            else:
                print("   Neon disabled.")

        except Exception as e:
             print(f"FAILURE: {e}")
             import traceback
             traceback.print_exc()

    asyncio.run(main())
    print("Test complete.")
except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()
except SystemExit as e:
    print(f"SystemExit: {e}")
