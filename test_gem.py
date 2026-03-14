import os
import json
from google import genai
import PIL.Image
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    # Use an existing image from uploads for testing
    image_path = "uploads/490f80a68fa441d4ba8dbe07f361e72c_images.jpeg"
    if not os.path.exists(image_path):
        print(f"Test image not found at {image_path}. Please ensure an image exists in uploads.")
        return

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("GEMINI_API_KEY not found in .env")
        return

    client = genai.Client(api_key=api_key)
    img = PIL.Image.open(image_path)
    
    prompt = """Analyze this plant image (leaf, fruit, or stem). 
Identify the plant species and any disease present. 
REQUIRED JSON FORMAT (no markdown blocks):
{
  "class_name": "Species + Disease",
  "confidence": 95.0,
  "symptoms": "Description",
  "damage": "Impact",
  "treatment": ["Step 1"],
  "prevention": "Prevention",
  "severity": "Low/Medium/High/Healthy"
}"""
    print("Calling Gemini...")
    try:
        response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents=[prompt, img]
        )
        print("Response text:")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini()
