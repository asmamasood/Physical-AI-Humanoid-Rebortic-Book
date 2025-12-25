import requests
import json
import sys
import uuid

# Configuration
API_URL = "http://localhost:8000/api/chat"
SELECTIVE_API_URL = "http://localhost:8000/api/selective-chat"

def print_help():
    print("\ncommands:")
    print("  /rag <query>       - Ask a question using RAG (Default)")
    print("  /select <text>|<query> - Simulate 'selective chat' (formatting: highlighted_text|question)")
    print("  /quit              - Exit")
    print("  /help              - Show this help\n")

def run_chat():
    print("🤖 RAG Chatboard Terminal Test")
    print(f"Connecting to: {API_URL}")
    print_help()

    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}\n")

    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["/quit", "/exit"]:
                print("Bye! 👋")
                break
            
            if user_input.lower() == "/help":
                print_help()
                continue

            # Determine Mode
            if user_input.startswith("/select "):
                # Selective Chat Mode
                raw_args = user_input[8:]
                if "|" not in raw_args:
                    print("⚠️  Format Error: Use /select <highlighted_text>|<question>")
                    continue
                
                selection_text, query = raw_args.split("|", 1)
                payload = {
                    "query": query.strip(),
                    "selection_text": selection_text.strip(),
                    "session_id": session_id,
                    "selection_meta": {"source": "terminal-test"}
                }
                url = SELECTIVE_API_URL
                mode_label = "SELECTIVE"
            else:
                # Normal RAG Mode
                query = user_input
                if user_input.startswith("/rag "):
                    query = user_input[5:]
                
                payload = {
                    "query": query,
                    "session_id": session_id,
                    "top_k": 5
                }
                url = API_URL
                mode_label = "RAG"

            # Send Request
            try:
                print(f"[{mode_label}] Sending request...", end="", flush=True)
                response = requests.post(url, json=payload, timeout=30)
                print(" Done.")

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer provided.")
                    citations = data.get("citations", [])

                    print(f"\nAI > {answer}\n")
                    
                    if citations:
                        print("--- Citations ---")
                        for idx, cit in enumerate(citations):
                            print(f"[{idx+1}] {cit.get('chapter', 'Unknown')} (Score: {cit.get('score', 'N/A')})")
                            print(f"    URL: {cit.get('source_url', 'N/A')}")
                        print("-----------------\n")
                else:
                    print(f"\n❌ API Error {response.status_code}: {response.text}\n")

            except requests.exceptions.ConnectionError:
                print("\n❌ Connection Failed: Is the backend running on http://localhost:8000?\n")
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    run_chat()
