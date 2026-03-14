import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

def test_naming_variants():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    # Try different prefixes and versions
    variants = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-flash-latest",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.0-pro"
    ]
    
    with open("naming_results.txt", "w") as f:
        for v in variants:
            f.write(f"Testing {v}...\n")
            try:
                # Use a very small prompt
                response = client.models.generate_content(
                    model=v,
                    contents="hi"
                )
                f.write(f"SUCCESS with {v}: {response.text.strip()}\n")
                print(f"WINNER: {v}")
            except Exception as e:
                f.write(f"FAILED with {v}: {str(e)}\n")
    
    print("Done testing variants. Check naming_results.txt")

if __name__ == "__main__":
    test_naming_variants()
