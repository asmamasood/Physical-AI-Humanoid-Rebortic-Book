import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Starting FINAL model check...")
working_model = None
# Try some common ones first for speed
common_models = [
    'models/gemini-1.5-flash',
    'models/gemini-1.5-flash-latest',
    'models/gemini-1.5-pro',
    'models/gemini-2.0-flash-exp',
    'models/gemini-2.0-flash-lite-preview-0815',
    'models/gemini-1.5-flash-8b'
]

for name in common_models:
    try:
        model = genai.GenerativeModel(name)
        response = model.generate_content("Respond with exactly the word OK")
        if "OK" in response.text.upper():
            working_model = name
            break
    except:
        continue

if not working_model:
    # Full scan
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            try:
                model = genai.GenerativeModel(m.name)
                response = model.generate_content("Respond with exactly the word OK")
                if "OK" in response.text.upper():
                    working_model = m.name
                    break
            except:
                continue

print(f"RESULT_WORKING_MODEL: {working_model}")
