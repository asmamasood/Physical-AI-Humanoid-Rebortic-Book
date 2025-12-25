import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_try = [
    'gemini-1.5-flash',
    'models/gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-pro'
]

for model_name in models_to_try:
    print(f"\nTrying model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello")
        print(f"SUCCESS: {response.text.strip()}")
        break
    except Exception as e:
        print(f"FAILED: {e}")
