#  AgroDetect AI – Plant Disease Classification Engine

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-orange?logo=tensorflow)](https://www.tensorflow.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

AgroDetect AI is a high-performance deep learning system designed to bridge the gap between advanced agricultural science and small-scale farming. By leveraging **MobileNetV2** architecture, it provides instant, accurate, and actionable plant disease diagnosis through a simple leaf image upload.

---

##  Why AgroDetect AI?

Crop diseases are a silent threat, often destroying entire harvests before the symptoms are correctly identified. AgroDetect AI empowers farmers with an "expert in their pocket," offering more than just a name—it provides a comprehensive recovery plan in the farmer's local language.

###  Key Features at a Glance

*    **Deep Learning Diagnostics**: Powered by a fine-tuned MobileNetV2 model trained on 87,000+ images with **95%+ validation accuracy**.
*    **Extensive Crop Support**: Identifies **38 distinct classes** across 14+ major crops including Tomato, Potato, Corn, Apple, Grape, and Orange.
*    **Truly Localized**: A multilingual interface supporting **English**, **Hindi (हिंदी)**, and **Telugu (తెలుగు)** to ensure accessibility for rural communities.
*    **Audio Guidance**: Integrated **gTTS (Google Text-to-Speech)** provides voice readouts of labels and treatments—perfect for hands-free field use.
*    **Actionable Insights**: Goes beyond detection to provide detailed **Symptoms**, **Crop Damage** reports, **Treatment** steps, and **Prevention** strategies.
*    **Inference Speed**: Optimized preprocessing and model execution ensure results in **under 2 seconds**.

---

##  The Technology Stack

*   **Backend**: Flask (Python)
*   **Deep Learning**: TensorFlow / Keras
*   **Computer Vision**: OpenCV (Image preprocessing & augmentation)
*   **AI Architecture**: MobileNetV2 (Transfer Learning)
*   **Audio**: gTTS (Google Text-to-Speech)
*   **Frontend**: Modern Vanilla CSS with Glassmorphism and Responsive Design

---

##  Project Structure

```text
AgroDetect-AI/
├── app.py                 # Flask server & Routing logic
├── disease_info.py        # Disease database & Translation engine
├── train_model.py         # Model training & Augmentation pipeline
├── mobilenetv2_best.keras # Pre-trained production model
├── static/                # CSS, client-side JS, and generated audio
├── templates/             # HTML5 templates (Home, Upload, Result, About)
└── requirements.txt       # Project dependencies
```

---

##  Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/AgroDetect-AI.git
cd AgroDetect-AI
```

### 2. Set Up Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Engine
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

---

##  Model Training & Dataset

The engine is trained on the **PlantVillage Dataset**, utilizing heavy data augmentation (Rotation, Zoom, Shear, and Horizontal Flips) to handle real-world lighting and camera angles.

- **Frozen Backbone**: MobileNetV2 (ImageNet)
- **Custom Head**: Global Average Pooling → Dropout (0.3) → Dense (256, ReLU) → Dense (38, Softmax)
- **Optimizer**: Adam (Learning Rate: 1e-4)

---

##  Contributing

Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---



##  Acknowledgments

- [PlantVillage Dataset](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset) for the incredible training resources.
- The Keras/TensorFlow teams for the MobileNetV2 implementation.
