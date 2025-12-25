import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

try:
    name = 'models/gemini-1.5-flash-8b'
    print(f"Info for {name}:")
    model_info = genai.get_model(name)
    print(f"Display Name: {model_info.display_name}")
    print(f"Methods: {model_info.supported_generation_methods}")
    
    print("\nAttempting simple generate_content...")
    model = genai.GenerativeModel(name)
    response = model.generate_content("Say hello")
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"FAILED: {e}")
