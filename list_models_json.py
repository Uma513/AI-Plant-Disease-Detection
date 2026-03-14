import os
import sys
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_models_to_json():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    
    models_data = []
    try:
        for m in client.models.list():
            # Convert model object to dict if possible, or just pick attributes
            m_info = {
                "name": getattr(m, 'name', 'N/A'),
                "base_model_id": getattr(m, 'base_model_id', 'N/A'),
                "version": getattr(m, 'version', 'N/A'),
                "display_name": getattr(m, 'display_name', 'N/A'),
                "description": getattr(m, 'description', 'N/A'),
            }
            models_data.append(m_info)
        
        with open("model_list.json", "w") as f:
            json.dump(models_data, f, indent=2)
        print("Successfully listed models to model_list.json")
    except Exception as e:
        print(f"Failed to list models: {e}")

if __name__ == "__main__":
    list_models_to_json()
