import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

def test_models():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    models_to_try = [
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-2.0-flash-lite",
        "gemini-1.5-pro"
    ]
    
    for model_name in models_to_try:
        print(f"Testing model: {model_name}...")
        sys.stdout.flush()
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="test"
            )
            print(f"SUCCESS with {model_name}")
            sys.stdout.flush()
        except Exception as e:
            print(f"FAILED with {model_name}: {str(e)[:200]}")
            sys.stdout.flush()

if __name__ == "__main__":
    test_models()
