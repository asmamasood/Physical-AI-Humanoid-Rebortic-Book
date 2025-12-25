import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Searching for functional models...")
winners = []
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            try:
                model = genai.GenerativeModel(m.name)
                response = model.generate_content("hi")
                if response.text:
                    winners.append(m.name)
                    print(f"FOUND: {m.name}")
            except:
                continue
except Exception as e:
    print(f"Error: {e}")

with open('winner.txt', 'w') as f:
    for w in winners:
        f.write(f"{w}\n")
print(f"Finished. Found {len(winners)} models.")
