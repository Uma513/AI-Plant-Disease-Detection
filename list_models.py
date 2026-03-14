import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("GEMINI_API_KEY not found in .env")
        return

    client = genai.Client(api_key=api_key)
    print("Listing available models...")
    try:
        # The new SDK has client.models.list()
        for m in client.models.list():
            if 'generateContent' in m.supported_methods:
                print(f"Model: {m.name}, Display Name: {m.display_name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_available_models()
