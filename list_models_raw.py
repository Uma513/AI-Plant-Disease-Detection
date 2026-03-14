import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_models_to_file():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    with open("model_list.txt", "w") as f:
        try:
            for m in client.models.list():
                f.write(f"Name: {m.name}, Methods: {m.supported_methods}\n")
            print("Successfully listed models to model_list.txt")
        except Exception as e:
            f.write(f"Error listing models: {str(e)}\n")
            print(f"Failed to list models: {e}")

if __name__ == "__main__":
    list_models_to_file()
