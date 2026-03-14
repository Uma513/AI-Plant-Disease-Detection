"""
disease_info.py  – Disease information database + translation dictionaries
"""
import json
import os


# ──────────────────────────────────────────────────────────────────────────────
# CLASS INDEX  (must match the order in which ImageDataGenerator builds classes)
# ──────────────────────────────────────────────────────────────────────────────
CLASS_NAMES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

# ──────────────────────────────────────────────────────────────────────────────
# DISEASE DATABASE  – keyed on class name
# ──────────────────────────────────────────────────────────────────────────────
DISEASE_DB = {
    "Apple___Apple_scab": {
        "name": "Apple Scab",
        "symptoms": "Olive-green to brown scabby lesions on leaves and fruit. Leaves may curl and drop early.",
        "damage": "Reduces fruit quality and yield. Severe infection can defoliate the tree.",
        "treatment": [
            "Apply fungicides (captan, myclobutanil) at green tip stage.",
            "Remove and destroy infected leaves and fruit.",
            "Prune for better air circulation.",
        ],
        "prevention": "Plant resistant varieties. Rake and destroy fallen leaves in autumn.",
        "severity": "Medium",
    },
    "Apple___Black_rot": {
        "name": "Apple Black Rot",
        "symptoms": "Purple spots on leaves enlarging with brown centres. Mummified fruits with black rot.",
        "damage": "Significant fruit loss; can kill young branches.",
        "treatment": [
            "Apply copper-based fungicides.",
            "Remove mummified fruits and cankers.",
            "Prune dead wood regularly.",
        ],
        "prevention": "Maintain orchard sanitation. Avoid wounds on trees.",
        "severity": "High",
    },
    "Apple___Cedar_apple_rust": {
        "name": "Cedar Apple Rust",
        "symptoms": "Bright orange-yellow spots on upper leaf surface; tube-like structures below.",
        "damage": "Causes early leaf drop and reduces fruit production.",
        "treatment": [
            "Apply fungicides (myclobutanil, mancozeb) in spring.",
            "Remove nearby juniper/cedar hosts if possible.",
        ],
        "prevention": "Plant rust-resistant apple varieties.",
        "severity": "Medium",
    },
    "Apple___healthy": {
        "name": "Healthy Apple Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed. Continue good farming practices."],
        "prevention": "Maintain regular monitoring and balanced nutrition.",
        "severity": "Low",
    },
    "Blueberry___healthy": {
        "name": "Healthy Blueberry Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed."],
        "prevention": "Maintain soil pH 4.5–5.5 and adequate irrigation.",
        "severity": "Low",
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "name": "Cherry Powdery Mildew",
        "symptoms": "White powdery coating on young leaves, shoots, and fruits.",
        "damage": "Stunted growth and reduced fruit quality.",
        "treatment": [
            "Apply sulphur-based or systemic fungicides.",
            "Remove infected shoots.",
        ],
        "prevention": "Improve air circulation. Avoid excessive nitrogen fertiliser.",
        "severity": "Medium",
    },
    "Cherry_(including_sour)___healthy": {
        "name": "Healthy Cherry Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed."],
        "prevention": "Regular monitoring and proper pruning.",
        "severity": "Low",
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "name": "Corn Gray Leaf Spot",
        "symptoms": "Rectangular grey to brown lesions parallel to leaf veins.",
        "damage": "Premature leaf death, yield losses up to 50% in severe cases.",
        "treatment": [
            "Apply foliar fungicides (strobilurin, triazole).",
            "Rotate crops with non-host plants.",
        ],
        "prevention": "Plant resistant hybrids. Avoid no-till in high-risk areas.",
        "severity": "High",
    },
    "Corn_(maize)___Common_rust_": {
        "name": "Corn Common Rust",
        "symptoms": "Small, oval, reddish-brown pustules on both leaf surfaces.",
        "damage": "Reduces photosynthesis; severe infections decrease yield.",
        "treatment": [
            "Apply fungicides at early infection stages.",
            "Use resistant hybrids.",
        ],
        "prevention": "Plant early and use resistant varieties.",
        "severity": "Medium",
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "name": "Corn Northern Leaf Blight",
        "symptoms": "Long, cigar-shaped grey-green lesions on leaves.",
        "damage": "Causes large leaf area loss; major yield reduction.",
        "treatment": [
            "Apply fungicides (propiconazole, azoxystrobin).",
            "Destroy crop debris after harvest.",
        ],
        "prevention": "Plant resistant hybrids. Practice crop rotation.",
        "severity": "High",
    },
    "Corn_(maize)___healthy": {
        "name": "Healthy Corn Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed."],
        "prevention": "Monitor regularly and maintain soil health.",
        "severity": "Low",
    },
    "Grape___Black_rot": {
        "name": "Grape Black Rot",
        "symptoms": "Tan spots with dark borders on leaves; fruit shrivels to black mummies.",
        "damage": "Can destroy entire grape clusters in wet seasons.",
        "treatment": [
            "Apply fungicides (mancozeb, myclobutanil) before infection.",
            "Remove mummified berries and infected leaves.",
        ],
        "prevention": "Maintain good canopy airflow. Sanitation is key.",
        "severity": "High",
    },
    "Grape___Esca_(Black_Measles)": {
        "name": "Grape Esca (Black Measles)",
        "symptoms": "Interveinal chlorosis and necrosis; tiger-stripe pattern on leaves; berry shrivelling.",
        "damage": "Progressive vine decline; can be fatal over time.",
        "treatment": [
            "Prune infected wood. Protect pruning wounds with fungicide paste.",
            "No fully curative treatment exists—focus on prevention.",
        ],
        "prevention": "Avoid large pruning wounds. Seal wounds immediately.",
        "severity": "High",
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "name": "Grape Leaf Blight",
        "symptoms": "Irregular dark brown spots, yellowing, and early leaf drop.",
        "damage": "Weakens vines and reduces subsequent year's yield.",
        "treatment": [
            "Apply copper fungicides.",
            "Remove fallen infected leaves promptly.",
        ],
        "prevention": "Ensure good drainage and canopy management.",
        "severity": "Medium",
    },
    "Grape___healthy": {
        "name": "Healthy Grape Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed."],
        "prevention": "Regular pruning and disease monitoring.",
        "severity": "Low",
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "name": "Citrus Greening (HLB)",
        "symptoms": "Asymmetric blotchy mottling on leaves; small, lopsided bitter fruit; yellow shoots.",
        "damage": "Kills citrus trees within a few years. No cure available.",
        "treatment": [
            "Remove and destroy infected trees to prevent spread.",
            "Control Asian citrus psyllid vector with insecticides.",
        ],
        "prevention": "Use certified disease-free nursery plants. Monitor for psyllid.",
        "severity": "High",
    },
    "Peach___Bacterial_spot": {
        "name": "Peach Bacterial Spot",
        "symptoms": "Small, water-soaked spots on leaves turning brown with yellow halos; fruit cracking.",
        "damage": "Defoliation and reduced fruit market value.",
        "treatment": [
            "Apply copper-based bactericides.",
            "Avoid overhead irrigation.",
        ],
        "prevention": "Plant resistant varieties. Apply preventive copper sprays.",
        "severity": "Medium",
    },
    "Peach___healthy": {
        "name": "Healthy Peach Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed."],
        "prevention": "Regular scouting and fertilisation.",
        "severity": "Low",
    },
    "Pepper,_bell___Bacterial_spot": {
        "name": "Bell Pepper Bacterial Spot",
        "symptoms": "Small water-soaked lesions on leaves and fruit; lesions turn brown and scabby.",
        "damage": "Causes leaf drop and unmarketable fruit.",
        "treatment": [
            "Apply copper bactericides weekly.",
            "Remove severely infected plants.",
        ],
        "prevention": "Use certified seed. Avoid working in wet fields.",
        "severity": "Medium",
    },
    "Pepper,_bell___healthy": {
        "name": "Healthy Bell Pepper Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed."],
        "prevention": "Balanced fertilisation and pest monitoring.",
        "severity": "Low",
    },
    "Potato___Early_blight": {
        "name": "Potato Early Blight",
        "symptoms": "Dark brown lesions with concentric rings (target-board pattern) on older leaves.",
        "damage": "Reduces leaf area; can cut yield by 20–30%.",
        "treatment": [
            "Apply chlorothalonil or mancozeb fungicides.",
            "Remove infected crop debris after harvest.",
        ],
        "prevention": "Crop rotation. Avoid overhead irrigation.",
        "severity": "Medium",
    },
    "Potato___Late_blight": {
        "name": "Potato Late Blight",
        "symptoms": "Water-soaked, dark lesions on leaves/stems; white mould on underside in humid conditions.",
        "damage": "Can destroy entire potato crop within days; caused the Irish Famine.",
        "treatment": [
            "Apply metalaxyl or cymoxanil fungicides immediately.",
            "Destroy infected plant material.",
            "Hill up soil around stems.",
        ],
        "prevention": "Plant certified seed tubers. Monitor weather for disease-friendly conditions.",
        "severity": "High",
    },
    "Potato___healthy": {
        "name": "Healthy Potato Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed."],
        "prevention": "Use certified seed tubers and practice crop rotation.",
        "severity": "Low",
    },
    "Raspberry___healthy": {
        "name": "Healthy Raspberry Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed."],
        "prevention": "Proper pruning and site selection.",
        "severity": "Low",
    },
    "Soybean___healthy": {
        "name": "Healthy Soybean Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed."],
        "prevention": "Crop rotation and soil testing.",
        "severity": "Low",
    },
    "Squash___Powdery_mildew": {
        "name": "Squash Powdery Mildew",
        "symptoms": "White powdery growth on upper leaf surfaces; leaves may yellow and die.",
        "damage": "Reduces photosynthesis and fruit development.",
        "treatment": [
            "Apply potassium bicarbonate or sulphur-based fungicides.",
            "Remove heavily infected leaves.",
        ],
        "prevention": "Plant resistant varieties. Ensure good air circulation.",
        "severity": "Medium",
    },
    "Strawberry___Leaf_scorch": {
        "name": "Strawberry Leaf Scorch",
        "symptoms": "Small, irregular purple spots on leaves; centres turn brown giving a scorched look.",
        "damage": "Reduces plant vigour and fruit production over time.",
        "treatment": [
            "Apply captan or myclobutanil fungicide.",
            "Remove and destroy old infected leaves.",
        ],
        "prevention": "Avoid overhead irrigation. Renovate beds after harvest.",
        "severity": "Medium",
    },
    "Strawberry___healthy": {
        "name": "Healthy Strawberry Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed."],
        "prevention": "Renovate beds annually and manage irrigation carefully.",
        "severity": "Low",
    },
    "Tomato___Bacterial_spot": {
        "name": "Tomato Bacterial Spot",
        "symptoms": "Small, water-soaked spots on leaves, stems, and fruit; spots turn brown with yellow haloes.",
        "damage": "Severe defoliation and reduced fruit quality.",
        "treatment": [
            "Apply copper bactericide + mancozeb mixture.",
            "Avoid overhead irrigation.",
            "Remove infected plant debris.",
        ],
        "prevention": "Use certified disease-free seed. Rotate crops yearly.",
        "severity": "Medium",
    },
    "Tomato___Early_blight": {
        "name": "Tomato Early Blight",
        "symptoms": "Dark brown concentric-ring lesions starting on older leaves.",
        "damage": "Progressive defoliation starting from bottom; reduces yield significantly.",
        "treatment": [
            "Apply chlorothalonil or copper fungicide every 7–10 days.",
            "Mulch around plants to prevent soil splash.",
            "Remove infected lower leaves.",
        ],
        "prevention": "Crop rotation. Stake plants for air circulation.",
        "severity": "Medium",
    },
    "Tomato___Late_blight": {
        "name": "Tomato Late Blight",
        "symptoms": "Greasy, dark lesions on leaves with white fuzzy spores; fruit turns brown and rots.",
        "damage": "Can decimate entire crop within a week in cool wet weather.",
        "treatment": [
            "Apply metalaxyl + chlorothalonil fungicide immediately.",
            "Remove and bury heavily infected plants.",
            "Avoid overhead watering.",
        ],
        "prevention": "Plant resistant varieties. Monitor during wet, cool periods.",
        "severity": "High",
    },
    "Tomato___Leaf_Mold": {
        "name": "Tomato Leaf Mold",
        "symptoms": "Yellow patches on upper leaf surface; olive-green mould on undersides.",
        "damage": "Reduces photosynthetic area; yields drop in severe infections.",
        "treatment": [
            "Apply copper fungicide.",
            "Ensure good greenhouse ventilation.",
            "Remove infected leaves.",
        ],
        "prevention": "Maintain humidity below 85%. Use resistant varieties.",
        "severity": "Medium",
    },
    "Tomato___Septoria_leaf_spot": {
        "name": "Tomato Septoria Leaf Spot",
        "symptoms": "Small circular spots with dark borders and light grey centres on lower leaves.",
        "damage": "Heavy defoliation reduces fruit size and sun-scalding of fruit.",
        "treatment": [
            "Apply chlorothalonil, mancozeb, or copper fungicide.",
            "Remove infected leaves immediately.",
            "Mulch soil to avoid splash",
        ],
        "prevention": "Crop rotation. Avoid working with wet plants.",
        "severity": "Medium",
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "name": "Tomato Spider Mites",
        "symptoms": "Tiny yellow speckling on leaves; fine webbing on undersides; bronzing of leaves.",
        "damage": "Rapid leaf death in hot, dry conditions. Major yield losses.",
        "treatment": [
            "Apply miticides (abamectin, bifenazate).",
            "Use neem oil or insecticidal soap.",
            "Introduce predatory mites (biological control).",
        ],
        "prevention": "Maintain proper irrigation. Avoid dusty conditions.",
        "severity": "High",
    },
    "Tomato___Target_Spot": {
        "name": "Tomato Target Spot",
        "symptoms": "Brown circular lesions with concentric rings resembling a target on leaves and fruit.",
        "damage": "Causes defoliation and unmarketable fruit.",
        "treatment": [
            "Apply tebuconazole or chlorothalonil fungicides.",
            "Remove infected plant material.",
        ],
        "prevention": "Avoid dense planting. Ensure good air circulation.",
        "severity": "Medium",
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "name": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "symptoms": "Upward curling of leaves, yellowing of leaf margins, stunted plant growth.",
        "damage": "Severely reduces yield; infected plants rarely recover.",
        "treatment": [
            "Remove and destroy infected plants.",
            "Control whitefly vector with insecticides (imidacloprid).",
            "Use reflective mulch to deter whiteflies.",
        ],
        "prevention": "Plant TYLCV-resistant varieties. Use insect-proof nets.",
        "severity": "High",
    },
    "Tomato___Tomato_mosaic_virus": {
        "name": "Tomato Mosaic Virus (ToMV)",
        "symptoms": "Mosaic pattern of light and dark green on leaves; leaf distortion; stunted growth.",
        "damage": "Reduces fruit yield; fruit may show internal browning.",
        "treatment": [
            "Remove and destroy infected plants.",
            "Disinfect tools with bleach solution.",
            "Control aphid/insect vectors.",
        ],
        "prevention": "Use certified virus-free seed. Wash hands before handling plants.",
        "severity": "High",
    },
    "Tomato___healthy": {
        "name": "Healthy Tomato Plant",
        "symptoms": "No disease symptoms detected.",
        "damage": "None.",
        "treatment": ["No treatment needed. Your plant is healthy!"],
        "prevention": "Continue monitoring. Maintain proper irrigation and fertilisation.",
        "severity": "Low",
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# SEVERITY COLOURS (for UI badges)
# ──────────────────────────────────────────────────────────────────────────────
SEVERITY_COLORS = {
    "Low": "#22c55e",
    "Medium": "#f59e0b",
    "High": "#ef4444",
}

# ──────────────────────────────────────────────────────────────────────────────
# TRANSLATION DICTIONARIES  (key phrases -> Telugu / Hindi)
# ──────────────────────────────────────────────────────────────────────────────

TRANSLATIONS = {
    "Symptoms": {"te": "లక్షణాలు", "hi": "लक्षण", "ta": "அறிகுறிகள்", "kn": "ಲಕ್ಷಣಗಳು", "ml": "ലക്ഷണങ്ങൾ", "mr": "लक्षणे", "bn": "উপসর্গ", "gu": "લક્ષણો", "es": "Síntomas"},
    "Crop Damage": {"te": "పంట నష్టం", "hi": "फसल नुकसान", "ta": "பயிர் சேதம்", "kn": "ಬೆಳೆ ಹಾನಿ", "ml": "വിള നാശം", "mr": "पिकाचे नुकसान", "bn": "ফসলের ক্ষতি", "gu": "પાક નુકસાન", "es": "Daño"},
    "Treatment": {"te": "చికిత్స", "hi": "उपचार", "ta": "சிகிச்சை", "kn": "ಚಿಕಿತ್ಸೆ", "ml": "ചികിത്സ", "mr": "उपचार", "bn": "চিকিৎসা", "gu": "સારવાર", "es": "Tratamiento"},
    "Prevention": {"te": "నివారణ", "hi": "रोकथाम", "ta": "தடுப்பு", "kn": "ತಡೆಗಟ್ಟುವಿಕೆ", "ml": "തടയൽ", "mr": "प्रतिबंध", "bn": "প্রতিরোধ", "gu": "નિવારણ", "es": "Prevención"},
    "Confidence": {"te": "నిర్ధారణ స్థాయి", "hi": "विश्वास स्तर", "ta": "நம்பிக்கை நிலை", "kn": "ನಂಬಿಕೆಯ ಮಟ್ಟ", "ml": "വിശ്വാസ്യത", "mr": "आत्मविश्वास पातळी", "bn": "নিশ্চয়তার মাত্রা", "gu": "આત્મવિશ્વાસ", "es": "Confianza"},
    "Severity": {"te": "తీవ్రత", "hi": "गंभीरता", "ta": "தீவிரம்", "kn": "ತೀವ್ರತೆ", "ml": "തീവ്രത", "mr": "तीव्रता", "bn": "তীব্রতা", "gu": "તીવ્રતા", "es": "Gravedad"},
    "Low": {"te": "తక్కువ", "hi": "कम", "ta": "குறைந்த", "kn": "ಕಡಿಮೆ", "ml": "കുറഞ്ഞ", "mr": "कमी", "bn": "কম", "gu": "ઓછું", "es": "Baja"},
    "Medium": {"te": "మధ్యమ", "hi": "मध्यम", "ta": "நடுத்தர", "kn": "ಮಧ್ಯಮ", "ml": "മിതമായ", "mr": "मध्यम", "bn": "মাঝারি", "gu": "મધ્યમ", "es": "Media"},
    "High": {"te": "అధిక", "hi": "अधिक", "ta": "அதிக", "kn": "ಹೆಚ್ಚು", "ml": "ഉയർന്ന", "mr": "उच्च", "bn": "বেশি", "gu": "ઉચ્ચ", "es": "Alta"},
    "Disease Detected": {"te": "వ్యాధి గుర్తించబడింది", "hi": "रोग पहचाना गया", "ta": "நோய் கண்டறியப்பட்டது", "kn": "ರೋಗ ಪತ್ತೆಯಾಗಿದೆ", "ml": "രോഗം കണ്ടെത്തി", "mr": "रोग आढळला", "bn": "রোগ শনাক্ত হয়েছে", "gu": "રોગ મળી આવ્યો", "es": "Enfermedad Detectada"},
    "Healthy Plant": {"te": "ఆరోగ్యకరమైన మొక్క", "hi": "स्वस्थ पौधा", "ta": "ஆரோக்கியமான செடி", "kn": "ಆರೋಗ್ಯಕರ ಸಸ್ಯ", "ml": "ആരോഗ്യകരമായ സസ്യം", "mr": "निरोगी वनस्पती", "bn": "সুস্থ গাছ", "gu": "તંદુરસ્ત છોડ", "es": "Planta Saludable"},
    "Please upload a clearer image for accurate diagnosis.": {
        "te": "ఖచ్చితమైన నిర్ధారణ కోసం దయచేసి స్పష్టమైన చిత్రాన్ని అప్‌లోడ్ చేయండి.",
        "hi": "सटीक निदान के लिए कृपया एक स्पष्ट छवि अपलोड करें।",
        "ta": "துல்லியமான நோயறிதலுக்கு தெளிவான படத்தைப் பதிவேற்றவும்.",
        "kn": "ನಿಖರವಾದ ರೋಗನಿರ್ಣಯಕ್ಕಾಗಿ ಸ್ಪಷ್ಟವಾದ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
        "ml": "വ്യക്തമായ ചിത്രം അപ്‌ലോഡ് ചെയ്യുക.",
        "mr": "स्पष्ट प्रतिमा अपलोड करा.",
        "bn": "পরিষ্কার ছবি আপলোড করুন।",
        "gu": "સ્પષ્ટ છબી અપલોડ કરો.",
        "es": "Por favor, sube una imagen más clara."
    },
    "Diagnosis Result": {"te": "నిర్ధారణ ఫలితాలు", "hi": "निदान परिणाम", "ta": "முடிவு", "kn": "ಫಲಿತಾಂಶ", "ml": "ഫലം", "mr": "निकाल", "bn": "ফলাফল", "gu": "પરિણામ", "es": "Resultado"},
    "AI analysis complete — review your detailed plant health report below": {
        "te": "AI విశ్లేషణ పూర్తయింది — మీ వివరణాత్మక నివేదికను సమీక్షించండి",
        "hi": "AI विश्लेषण पूरा हो गया है - नीचे अपनी रिपोर्ट की समीक्षा करें",
        "ta": "AI பகுப்பாய்வு முடிந்தது — அறிக்கையை மதிப்பாய்வு செய்யவும்",
        "kn": "AI ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ - ವರದಿಯನ್ನು ಪರಿಶೀಲಿಸಿ",
        "ml": "AI വിശകലനം പൂർത്തിയായി — റിപ്പോർട്ട് അവലോകനം ചെയ്യുക",
        "mr": "एआय विश्लेषण पूर्ण झाले - अहवालाचे पुनरावलोकन करा",
        "bn": "AI বিশ্লেষণ সম্পূর্ণ — প্রতিবেদনটি পর্যালোচনা করুন",
        "gu": "AI વિશ્લેષણ પૂર્ણ થયું - અહેવાલની સમીક્ષા કરો",
        "es": "Análisis IA completo."
    },
    "Top Predictions": {"te": "అగ్ర అంచనాలు", "hi": "शीर्ष भविष्यवाणियां", "ta": "சிறந்த கணிப்புகள்", "kn": "ಉನ್ನತ ಮುನ್ಸೂಚನೆಗಳು", "ml": "പ്രധാന പ്രവചനങ്ങൾ", "mr": "शीर्ष अंदाज", "bn": "ভবিষ্যদ্বাণী", "gu": "આગાહીઓ", "es": "Predicciones"},
    "Voice Diagnosis": {"te": "వాయిస్ నిర్ధారణ", "hi": "आवाज निदान", "ta": "குரல் நோயறிதல்", "kn": "ಧ್ವನಿ ರೋಗನಿರ್ಣಯ", "ml": "വോയ്സ് രോഗനിർണ്ണയം", "mr": "व्हॉ이스 निदान", "bn": "ভয়েস নির্ণয়", "gu": "વૉઇસ નિદાન", "es": "Voz"},
    "Read Aloud (Browser)": {"te": "బిగ్గరగా చదవండి", "hi": "ज़ोर से पढ़ें", "ta": "சத்தமாகப் படியுங்கள்", "kn": "ಜೋರಾಗಿ ಓದಿ", "ml": "ഉറക്കെ വായിക്കുക", "mr": "मोठ्याने वाचा", "bn": "জোরে পড়ুন", "gu": "જોરથી વાંચો", "es": "Leer"},
    "Scan Another Plant": {"te": "మరో మొక్కను స్కాన్ చేయండి", "hi": "एक और पौधा स्कैन करें", "ta": "மற்றொரு செடியை ஸ்கேன் செய்யவும்", "kn": "ಮತ್ತೊಂದು ಸಸ್ಯವನ್ನು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ", "ml": "മറ്റൊരു സസ്യം സ്കാൻ ചെയ്യുക", "mr": "दुसऱ्या वनस्पतीचे स्कॅन करा", "bn": "আরেকটি গাছ স্ক্যান করুন", "gu": "બીજો છોડ સ્કેન કરો",
    "es": "Escanear"},
    "Change Language": {"te": "భాషను మార్చండి", "hi": "भाषा बदलें", "ta": "மொழியை மாற்றவும்", "kn": "ಭಾಷೆ ಬದಲಾಯಿಸಿ", "ml": "ഭാഷ മാറ്റുക", "mr": "भाषा बदला", "bn": "ভাষা পরিবর্তন করুন", "gu": "ભાષા બદલો", "es": "Idioma"},
    "Stop": {"te": "ఆపు", "hi": "रुकें", "ta": "நிறுத்து", "kn": "ನಿಲ್ಲಿಸು", "ml": "നിർത്തുക", "mr": "थांबा", "bn": "থামুন", "gu": "રોકો", "es": "Detener"},
}

# Per-disease name translations (a representative subset)
DISEASE_NAME_TRANSLATIONS = {
    "Tomato Late Blight": {"te": "టమాటో అంటు వ్యాధి", "hi": "टमाटर अंगमारी"},
    "Tomato Early Blight": {"te": "టమాటో ముందస్తు అంటు", "hi": "टमाटर अगेती झुलसा"},
    "Tomato Leaf Mold": {"te": "టమాటో ఆకు అచ్చు", "hi": "टमाटर पत्ती फफूंद"},
    "Potato Late Blight": {"te": "బంగాళాదుంప అంటు వ్యాధి", "hi": "आलू पछेती झुलसा"},
    "Potato Early Blight": {"te": "బంగాళాదుంప ముందస్తు", "hi": "आलू अगेती झुलसा"},
    "Corn Gray Leaf Spot": {"te": "మొక్కజొన్న బూడిద మచ్చ", "hi": "मक्का ग्रे पत्ती धब्बा"},
    "Citrus Greening (HLB)": {"te": "నిమ్మకాయ పచ్చదనం", "hi": "नींबू हरितिमा"},
    "Healthy Tomato Plant": {"te": "ఆరోగ్యకరమైన టమాటో మొక్క", "hi": "स्वस्थ टमाटर पौधा"},
    "Healthy Potato Plant": {"te": "ఆరోగ్యకరమైన బంగాళాదుంప", "hi": "स्वस्थ आलू पौधा"},
    "Healthy Apple Plant": {"te": "ఆరోగ్యకరమైన యాపిల్ మొక్క", "hi": "स्वस्थ सेब पौधा"},
}


def get_disease_info(class_name: str) -> dict:
    """Return disease info dict for a given class label."""
    return DISEASE_DB.get(class_name, {
        "name": class_name.replace("___", " - ").replace("_", " "),
        "symptoms": "Information not available.",
        "damage": "Information not available.",
        "treatment": ["Consult your local agricultural extension officer."],
        "prevention": "Monitor plants regularly.",
        "severity": "Medium",
    })


def translate_label(label: str, lang: str) -> str:
    """Translate a UI label to the target language."""
    if lang == "en":
        return label
    entry = TRANSLATIONS.get(label, {})
    return entry.get(lang, label)


def translate_disease_name(name: str, lang: str) -> str:
    """Translate a disease name to the target language."""
    if lang == "en":
        return name
    entry = DISEASE_NAME_TRANSLATIONS.get(name, {})
    if lang in entry:
        return entry[lang]
    # Fallback to dynamic translation if not in dictionary
    return translate_text(name, lang)


# ──────────────────────────────────────────────────────────────────────────────
# TRANSLATION ENGINE  (Gemini-powered, disk-cached, English fallback)
# ──────────────────────────────────────────────────────────────────────────────

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations_cache.json")
TRANSLATION_CACHE: dict = {}

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as _f:
            TRANSLATION_CACHE = json.load(_f)
    except Exception:
        pass


def _save_cache() -> None:
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as _f:
            json.dump(TRANSLATION_CACHE, _f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# Lazy-init Gemini translator (reads key from env at first use)
_GEMINI_TRANSLATE_CLIENT = None

def _get_gemini_client():
    global _GEMINI_TRANSLATE_CLIENT
    if _GEMINI_TRANSLATE_CLIENT is not None:
        return _GEMINI_TRANSLATE_CLIENT
    try:
        from google import genai
        key = os.environ.get("GEMINI_API_KEY", "")
        if not key:
            return None
        _GEMINI_TRANSLATE_CLIENT = genai.Client(api_key=key)
    except Exception:
        _GEMINI_TRANSLATE_CLIENT = None
    return _GEMINI_TRANSLATE_CLIENT


# Exported language name map for prompt building
LANG_NAMES = {
    "te": "Telugu", 
    "hi": "Hindi",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "es": "Spanish"
}
_LANG_NAMES = LANG_NAMES 


def translate_text(text: str, lang: str) -> str:
    """
    Translate *text* to *lang* (te / hi) using Gemini API.
    Results are aggressively cached to disk so each phrase is only translated once.
    Falls back to the original English text on any error.
    """
    if lang == "en" or not text:
        return text

    cache_key = f"{lang}|{text}"
    if cache_key in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[cache_key]

    client = _get_gemini_client()
    if client is None:
        # Gemini unavailable – return English
        return text

    # Map code to full name for the prompt
    lang_name = _LANG_NAMES.get(lang, lang)
    prompt = (
        f"Translate the following English agricultural text to {lang_name}. "
        f"Return ONLY the translated text with no extra explanation:\n\n{text}"
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        result = response.text.strip()
        if result:
            TRANSLATION_CACHE[cache_key] = result
            _save_cache()
            return result
    except Exception as e:
        print(f"Gemini translation error: {e}")

    return text

