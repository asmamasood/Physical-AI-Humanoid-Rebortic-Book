import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL_NAME")

print(f"API Key: {api_key[:20]}...")
print(f"Model: {model_name}")

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say hello in one word")
    print(f"\nSuccess! Response: {response.text}")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    print(traceback.format_exc())
