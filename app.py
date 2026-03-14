"""
app.py – PlantCare AI  Flask backend  (v3 – single-prompt Gemini for speed + localization)
"""

import os

# ── Load .env file (GEMINI_API_KEY, SECRET_KEY, etc.) ─────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; rely on system environment variables

import uuid
import json
import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from flask import (Flask, render_template, request,
                   redirect, url_for, jsonify,
                   send_from_directory, session)
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

from disease_info import (CLASS_NAMES, get_disease_info,
                           translate_label, translate_disease_name,
                           SEVERITY_COLORS, DISEASE_DB, translate_text,
                           LANG_NAMES)

# ── Gemini (optional – supreme accuracy) ──────────────────────────────────────
try:
    from google import genai as _genai_module
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        _gemini_client = _genai_module.Client(api_key=GEMINI_API_KEY)
        GENAI_AVAILABLE = True
    else:
        _gemini_client = None
        GENAI_AVAILABLE = False
except ImportError:
    _gemini_client = None
    GENAI_AVAILABLE = False


# ── gTTS (optional – voice output) ────────────────────────────────────────────
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR      = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
STATIC_AUDIO  = BASE_DIR / "static" / "audio"
MODEL_PATH    = BASE_DIR / "mobilenetv2_best.keras"
ALLOWED_EXTS  = {"png", "jpg", "jpeg", "webp", "bmp"}
IMG_SIZE      = (224, 224)

UPLOAD_FOLDER.mkdir(exist_ok=True)
STATIC_AUDIO.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "plantcare-ai-secret-2024")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

# ─────────────────────────────────────────────────────────────────────────────
# Model loading
# ─────────────────────────────────────────────────────────────────────────────
model = None


def load_keras_model():
    global model
    if MODEL_PATH.exists():
        try:
            model = load_model(str(MODEL_PATH))
            logger.info(" Model loaded from %s", MODEL_PATH)
        except Exception as exc:
            logger.error("  Could not load model: %s", exc)
    else:
        logger.warning("  Model not found at %s – demo mode active.", MODEL_PATH)


load_keras_model()


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS


def preprocess_image(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, IMG_SIZE)
    img = img_to_array(img) / 255.0
    return np.expand_dims(img, axis=0)


def predict_disease(image_path: str, lang: str = "en") -> dict:
    """
    Single-prompt Gemini call: identifies the plant AND returns all text already
    in the requested language. Falls back to the local MobileNetV2 model.
    """
    if GENAI_AVAILABLE and _gemini_client is not None:
        try:
            import PIL.Image
            img = PIL.Image.open(image_path)

            # Resolve language name for the prompt
            lang_name = LANG_NAMES.get(lang, "English") if lang != "en" else "English"

            prompt = f"""Analyze this plant image (leaf, fruit, or stem).
Identify the plant species and any disease present.
If the plant is healthy, clearly state 'Healthy'.
If the image does not show a plant or fruit, identify what it is but note it is not a plant.

IMPORTANT: You MUST provide ALL text values (class_name, symptoms, damage, treatment steps, prevention) in {lang_name}.

REQUIRED JSON FORMAT (no markdown blocks, no extra text):
{{
  "class_name": "Species + Disease in {lang_name}",
  "confidence": 95.0,
  "symptoms": "Visible symptoms in {lang_name}",
  "damage": "Crop impact in {lang_name}",
  "treatment": ["Step 1 in {lang_name}", "Step 2 in {lang_name}"],
  "prevention": "Prevention advice in {lang_name}",
  "severity": "Low/Medium/High/Healthy"
}}"""

            response = _gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, img]
            )
            text = response.text.strip()

            # Strip markdown code fences if present
            if "```json" in text:
                text = text.split("```json")[-1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].strip()

            data = json.loads(text)

            # Ensure treatment is always a list
            treatment = data.get("treatment", ["No specific treatment required."])
            if isinstance(treatment, str):
                treatment = [treatment]

            return {
                "class_name": data.get("class_name", "Unknown Plant/Object"),
                "confidence": float(data.get("confidence", 90.0)),
                "top3": [{"label": data.get("class_name", "Detection"),
                          "prob": float(data.get("confidence", 90.0))}],
                "demo": False,
                "gemini_data": {
                    "class_name": data.get("class_name"),
                    "symptoms":   data.get("symptoms"),
                    "damage":     data.get("damage"),
                    "treatment":  treatment,
                    "prevention": data.get("prevention"),
                    "severity":   data.get("severity", "Medium")
                }
            }
        except Exception as e:
            logger.error(f"Gemini API error (falling back to local model): {e}")

    # ── Local MobileNetV2 fallback ─────────────────────────────────────────────
    if model is None:
        demo_class = "Tomato___Late_blight"
        return {
            "class_name": demo_class,
            "confidence": 0.0,
            "top3": [{"label": demo_class.replace("___", " – ").replace("_", " "), "prob": 0.0}],
            "demo": True,
        }

    x = preprocess_image(image_path)
    preds = model.predict(x, verbose=0)[0]
    idx = int(np.argmax(preds))
    confidence = float(preds[idx])
    top3_idx = np.argsort(preds)[::-1][:3]
    top3 = [
        {"label": CLASS_NAMES[i].replace("___", " – ").replace("_", " "),
         "prob": round(float(preds[i]) * 100, 1)}
        for i in top3_idx
    ]
    return {
        "class_name": CLASS_NAMES[idx],
        "confidence": round(confidence * 100, 1),
        "top3": top3,
        "demo": False,
    }


def generate_voice(text: str, lang_code: str = "en") -> Optional[str]:
    """Generate TTS audio and return web path. Falls back to None gracefully."""
    if not GTTS_AVAILABLE:
        return None
    try:
        gtts_lang_map = {
            "en": "en", "hi": "hi", "te": "te",
            "ta": "ta", "kn": "kn", "ml": "ml",
            "mr": "mr", "bn": "bn", "gu": "gu", "es": "es"
        }
        gtts_lang = gtts_lang_map.get(lang_code, "en")
        audio_file = STATIC_AUDIO / f"{uuid.uuid4().hex}.mp3"
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(str(audio_file))
        return f"/static/audio/{audio_file.name}"
    except Exception as exc:
        logger.warning("TTS failed: %s", exc)
        return None


def build_result_context(class_name: str, confidence: float,
                          top3: list, image_filename: str,
                          lang: str, is_demo: bool = False,
                          gemini_data: dict = None) -> dict:
    """Build the full template context for the result page."""
    info = get_disease_info(class_name).copy()

    if gemini_data:
        # Gemini already returned everything in the correct language —
        # no secondary translation API calls needed (much faster!)
        info["name"]       = gemini_data.get("class_name", info["name"])
        info["symptoms"]   = gemini_data.get("symptoms",   info["symptoms"])
        info["damage"]     = gemini_data.get("damage",     info["damage"])
        info["treatment"]  = gemini_data.get("treatment",  info["treatment"])
        if isinstance(info["treatment"], str):
            info["treatment"] = [info["treatment"]]
        info["prevention"] = gemini_data.get("prevention", info["prevention"])
        severity_raw       = gemini_data.get("severity", info.get("severity", "Medium"))
        info["severity"]   = (severity_raw or "Medium").capitalize()

        disease_name_translated = info["name"]
        symptoms_translated     = info["symptoms"]
        damage_translated       = info["damage"]
        prevention_translated   = info["prevention"]
        treatment_translated    = info["treatment"]
    else:
        # Fallback: local model output is English, translate via Gemini
        disease_name_translated = translate_disease_name(info["name"], lang)
        symptoms_translated     = translate_text(info["symptoms"],   lang)
        damage_translated       = translate_text(info["damage"],     lang)
        prevention_translated   = translate_text(info["prevention"], lang)
        treatment_translated    = [translate_text(t, lang) for t in info["treatment"]]

    severity_translated = translate_label(info.get("severity", "Medium"), lang)

    # Translate UI button/heading labels from the static dictionary (instant, no API)
    label_keys = [
        "Symptoms", "Crop Damage", "Treatment", "Prevention",
        "Confidence", "Severity", "Disease Detected", "Healthy Plant",
        "Please upload a clearer image for accurate diagnosis.",
        "Low", "Medium", "High",
        "Diagnosis Result",
        "AI analysis complete — review your detailed plant health report below",
        "Top Predictions", "Voice Diagnosis", "Read Aloud (Browser)",
        "Scan Another Plant", "Change Language", "Stop"
    ]
    label_map = {k: translate_label(k, lang) for k in label_keys}

    disease_detected_txt = label_map.get("Disease Detected", "Disease Detected")
    confidence_txt       = label_map.get("Confidence", "Confidence")
    severity_txt         = label_map.get("Severity", "Severity")
    symptoms_txt         = label_map.get("Symptoms", "Symptoms")
    damage_txt           = label_map.get("Crop Damage", "Crop Damage")
    treatment_txt        = label_map.get("Treatment", "Treatment")
    prevention_txt       = label_map.get("Prevention", "Prevention")

    # Build voice narration text (all already translated)
    voice_text = (
        f"{disease_detected_txt}: {disease_name_translated}. "
        f"{confidence_txt}: {confidence} percent. "
        f"{severity_txt}: {severity_translated}. "
        f"{symptoms_txt}: {symptoms_translated}. "
        f"{damage_txt}: {damage_translated}. "
        f"{treatment_txt}: {'. '.join(treatment_translated)}. "
        f"{prevention_txt}: {prevention_translated}."
    )
    audio_url = generate_voice(voice_text, lang)

    severity_color = SEVERITY_COLORS.get(info["severity"], "#f59e0b")
    low_confidence = (confidence < 50.0) and not is_demo

    return dict(
        image_filename=image_filename,
        class_name=class_name,
        disease_name=info["name"],
        disease_name_translated=disease_name_translated,
        confidence=confidence,
        symptoms=symptoms_translated,
        damage=damage_translated,
        treatment=treatment_translated,
        prevention=prevention_translated,
        severity=info["severity"],
        severity_color=severity_color,
        top3=top3,
        lang=lang,
        label=label_map,
        low_confidence=low_confidence,
        audio_url=audio_url,
        is_demo=is_demo,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("upload.html", error="No file selected.")

        file = request.files["file"]
        if not file or file.filename == "":
            return render_template("upload.html", error="No file selected.")

        if not allowed_file(file.filename):
            return render_template("upload.html",
                                   error="Invalid file type. Please upload PNG, JPG, or JPEG.")

        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = str(UPLOAD_FOLDER / filename)
        file.save(filepath)

        lang = request.form.get("lang", "en")

        # Single Gemini call: detect + translate in one shot
        pred = predict_disease(filepath, lang)

        session["pred"] = {
            "class_name":     pred["class_name"],
            "confidence":     pred["confidence"],
            "top3":           pred["top3"],
            "image_filename": filename,
            "demo":           pred.get("demo", False),
            "gemini_data":    pred.get("gemini_data", None)
        }

        return redirect(url_for("result", filename=filename, lang=lang))

    return render_template("upload.html")


@app.route("/result/<filename>")
def result(filename: str):
    """
    GET /result/<filename>?lang=en|te|hi|ta|kn|ml|mr|bn|gu|es

    Reads prediction from session and renders the result page.
    Changing ?lang= re-renders with translated UI labels (fast, static dict).
    """
    pred = session.get("pred")

    if not pred or pred.get("image_filename") != filename:
        return redirect(url_for("upload"))

    lang = request.args.get("lang", "en")
    if lang not in ("en", "te", "hi", "ta", "kn", "ml", "mr", "bn", "gu", "es"):
        lang = "en"

    ctx = build_result_context(
        class_name=pred["class_name"],
        confidence=pred["confidence"],
        top3=pred["top3"],
        image_filename=filename,
        lang=lang,
        is_demo=pred.get("demo", False),
        gemini_data=pred.get("gemini_data", None)
    )
    return render_template("result.html", **ctx)


@app.route("/uploads/<filename>")
def uploaded_file(filename: str):
    return send_from_directory(str(UPLOAD_FOLDER), filename)


# ── Voice generation API ──────────────────────────────────────────────────────
@app.route("/api/voice")
def api_voice():
    text = request.args.get("text", "")
    lang = request.args.get("lang", "en")
    if not text:
        return jsonify({"error": "No text"}), 400
    url = generate_voice(text, lang)
    if url:
        return jsonify({"url": url})
    return jsonify({"error": "TTS unavailable"}), 503


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """JSON API endpoint for programmatic access."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = str(UPLOAD_FOLDER / filename)
    file.save(filepath)
    lang = request.args.get("lang", "en")
    pred = predict_disease(filepath, lang)
    info = get_disease_info(pred["class_name"])
    return jsonify({
        "class_name":   pred["class_name"],
        "disease_name": info["name"],
        "confidence":   pred["confidence"],
        "severity":     info["severity"],
        "symptoms":     info["symptoms"],
        "treatment":    info["treatment"],
        "prevention":   info["prevention"],
        "top3":         pred["top3"],
    })


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
