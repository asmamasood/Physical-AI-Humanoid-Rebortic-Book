import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models = [
    'models/gemini-1.5-flash',
    'models/gemini-1.5-flash-8b',
    'models/gemini-2.0-flash-exp',
    'models/gemini-1.0-pro'
]

for name in models:
    print(f"Testing {name}:", end=" ", flush=True)
    try:
        model = genai.GenerativeModel(name)
        response = model.generate_content("hi")
        print(f"SUCCESS: {response.text.strip()}")
    except Exception as e:
        print(f"ERROR: {str(e)[:100]}")
