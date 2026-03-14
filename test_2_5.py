import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

def test_2_5():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    # Try the 2.5 model from the json list
    model_name = "gemini-2.5-flash"
    print(f"Testing {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'PlantCare AI is ready'"
        )
        print(f"SUCCESS: {response.text.strip()}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_2_5()
