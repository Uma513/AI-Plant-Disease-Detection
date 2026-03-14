import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def test():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    models = ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
    results = []
    for m in models:
        try:
            client.models.generate_content(model=m, contents="hi")
            results.append(f"{m}: SUCCESS")
        except Exception as e:
            results.append(f"{m}: FAILED ({str(e)[:50]})")
    
    with open("final_test.txt", "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    test()
