import os
import cohere
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))
texts = ["This is a test."]
response = co.embed(
    texts=texts,
    model="embed-english-v3.0",
    input_type="search_document"
)
print(f"Model: embed-english-v3.0")
print(f"Embedding segments: {len(response.embeddings)}")
print(f"Dimensions: {len(response.embeddings[0])}")
