import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model_name = "models/gemini-1.5-flash-8b"
model = genai.GenerativeModel(model_name)

# Mimic the actual prompt structure
prompt = """You are a helpful AI assistant for the "Physical AI & Humanoid Robotics" textbook.
Your role is to answer questions based ONLY on the provided context from the book.

INSTRUCTIONS:
1. Answer the user's question using ONLY information from the provided context chunks.
2. For each piece of information you use, cite the source using this format: [module:chapter:chunk_id]
3. If the answer is not found in the provided context, say: "I couldn't find this information in the book."
4. Be concise but comprehensive.
5. Do not make up information or use knowledge outside the provided context.

CONTEXT CHUNKS:
[test:test:test]
Physical AI is the integration of AI into physical systems like robots.

USER QUESTION: What is Physical AI?

Provide a helpful answer with citations:"""

print(f"Testing {model_name} with full prompt...")
try:
    response = model.generate_content(prompt)
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"FAILED: {e}")
