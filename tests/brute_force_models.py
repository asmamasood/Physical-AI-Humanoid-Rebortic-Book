import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Starting brute force model check...")
try:
    models = genai.list_models()
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"Testing model: {m.name}...", end=" ", flush=True)
            try:
                model = genai.GenerativeModel(m.name)
                response = model.generate_content("Say hello")
                print(f"SUCCESS: {response.text.strip()[:20]}...")
            except Exception as e:
                print(f"FAIL: {str(e)[:50]}...")
except Exception as e:
    print(f"Critical Error: {e}")
