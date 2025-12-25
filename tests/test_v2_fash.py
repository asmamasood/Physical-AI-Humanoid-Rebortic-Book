import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

try:
    print("Trying models/gemini-2.0-flash-exp...")
    model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
    response = model.generate_content("Say hello")
    print(f"SUCCESS: {response.text.strip()}")
except Exception as e:
    print(f"FAILED models/gemini-2.0-flash-exp: {e}")

try:
    print("\nTrying models/gemini-1.5-flash-latest...")
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    response = model.generate_content("Say hello")
    print(f"SUCCESS: {response.text.strip()}")
except Exception as e:
    print(f"FAILED models/gemini-1.5-flash-latest: {e}")
