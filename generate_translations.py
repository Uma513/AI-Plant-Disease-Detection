import json
import time
from deep_translator import GoogleTranslator
from disease_info import DISEASE_DB, CLASS_NAMES

# Initialize translators
translator_te = GoogleTranslator(source='en', target='te')
translator_hi = GoogleTranslator(source='en', target='hi')


def translate_text(text, translator):
    if not text or text == "None." or text == "None":
        if translator.target == 'te': return "ఏమీలేదు."
        if translator.target == 'hi': return "कुछ नहीं।"
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"Translation failed for '{text[:20]}...': {e}")
        return text


translated_db = {}

print("Starting translations. This might take a minute...")
total = len(CLASS_NAMES)

for idx, class_name in enumerate(CLASS_NAMES):
    print(f"Translating [{idx+1}/{total}]: {class_name}")
    info = DISEASE_DB.get(class_name, {})
    if not info:
        print(f"  Skipping {class_name} - not in DB")
        continue

    # English original
    translated_db[class_name] = {
        "en": info
    }

    # Telugu translation
    te_info = {
        "name": translate_text(info["name"], translator_te),
        "symptoms": translate_text(info["symptoms"], translator_te),
        "damage": translate_text(info["damage"], translator_te),
        "treatment": [translate_text(step, translator_te) for step in info["treatment"]],
        "prevention": translate_text(info["prevention"], translator_te),
        "severity": info["severity"] # UI translates this separately
    }
    translated_db[class_name]["te"] = te_info

    # Hindi translation
    hi_info = {
        "name": translate_text(info["name"], translator_hi),
        "symptoms": translate_text(info["symptoms"], translator_hi),
        "damage": translate_text(info["damage"], translator_hi),
        "treatment": [translate_text(step, translator_hi) for step in info["treatment"]],
        "prevention": translate_text(info["prevention"], translator_hi),
        "severity": info["severity"]
    }
    translated_db[class_name]["hi"] = hi_info

    # small sleep to avoid rate limiting
    time.sleep(0.5)

# Save to JSON
with open('disease_db_translated.json', 'w', encoding='utf-8') as f:
    json.dump(translated_db, f, ensure_ascii=False, indent=2)

print("\nTranslations complete! Saved to disease_db_translated.json")
