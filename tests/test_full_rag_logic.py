import asyncio
import os
import traceback
from backend.app.config import get_settings
from backend.app.cohere_client import CohereEmbedder
from backend.app.qdrant_client import QdrantService
from backend.app.gemini_agent import GeminiAgent
from dotenv import load_dotenv

load_dotenv()

async def test_logic():
    try:
        query = "What are Nodes in ROS 2?"
        print(f"Query: {query}")
        
        # 1. Embed
        print("Embedding...")
        embedder = CohereEmbedder()
        vector = await embedder.embed_query(query)
        print(f"Vector size: {len(vector)}")
        
        # 2. Search
        print("Searching...")
        qdrant = QdrantService()
        chunks = await qdrant.search_chunks(query_embedding=vector, top_k=3)
        print(f"Found {len(chunks)} chunks")
        for c in chunks:
            print(f"- {c['chapter']} (Score: {c['score']})")
        
        if not chunks:
            print("No chunks found. Stopping.")
            return

        # 3. LLM
        print("Generating answer...")
        agent = GeminiAgent()
        print(f"Using model: {agent.model.model_name}")
        answer, citations = await agent.generate_rag_answer(query, chunks)
        print(f"\nAnswer: {answer}")
        print(f"Citations: {len(citations)}")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_logic())
