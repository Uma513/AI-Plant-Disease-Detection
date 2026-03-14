import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

def single_test():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    # Try with explicit models/ prefix
    model_name = "models/gemini-1.5-flash"
    print(f"Testing {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="hi"
        )
        print(f"SUCCESS: {response.text.strip()}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    single_test()
