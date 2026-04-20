"""
Configuration — CropGuard AI
All settings: DB, Model, Mail, Upload, Disease Classes
"""

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cropguard-secret-bca-aiml-2026')

    # ── Database ──────────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'database', 'cropguard.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── File Uploads ──────────────────────────────────────────────────────────
    UPLOAD_FOLDER       = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH  = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS  = {'png', 'jpg', 'jpeg', 'webp'}

    # ── Model ─────────────────────────────────────────────────────────────────
    MODEL_PATH           = os.path.join(BASE_DIR, 'model', 'saved_model', 'crop_cnn.h5')
    IMAGE_SIZE           = (224, 224)
    CONFIDENCE_THRESHOLD = 0.70

    # ── Session ───────────────────────────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(hours=4)
    SESSION_COOKIE_SAMESITE    = 'Lax'
    SESSION_COOKIE_SECURE      = False   # Set True in production with HTTPS

    # ── Email / Alert Settings ────────────────────────────────────────────────
    MAIL_SERVER    = os.environ.get('MAIL_SERVER',   'smtp.gmail.com')
    MAIL_PORT      = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS   = True
    MAIL_USERNAME  = os.environ.get('MAIL_USERNAME', '')   # your Gmail
    MAIL_PASSWORD  = os.environ.get('MAIL_PASSWORD', '')   # app password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', 'cropguard@example.com')

    # Alert threshold — send email if confidence exceeds this and crop is diseased
    ALERT_CONFIDENCE_THRESHOLD = 0.80

    # ── PlantVillage Disease Classes (38) ─────────────────────────────────────
    DISEASE_CLASSES = [
        "Apple___Apple_scab",           "Apple___Black_rot",
        "Apple___Cedar_apple_rust",     "Apple___healthy",
        "Blueberry___healthy",          "Cherry___Powdery_mildew",
        "Cherry___healthy",             "Corn___Cercospora_leaf_spot",
        "Corn___Common_rust",           "Corn___Northern_Leaf_Blight",
        "Corn___healthy",               "Grape___Black_rot",
        "Grape___Esca_Black_Measles",   "Grape___Leaf_blight",
        "Grape___healthy",              "Orange___Haunglongbing",
        "Peach___Bacterial_spot",       "Peach___healthy",
        "Pepper___Bacterial_spot",      "Pepper___healthy",
        "Potato___Early_blight",        "Potato___Late_blight",
        "Potato___healthy",             "Raspberry___healthy",
        "Soybean___healthy",            "Squash___Powdery_mildew",
        "Strawberry___Leaf_scorch",     "Strawberry___healthy",
        "Tomato___Bacterial_spot",      "Tomato___Early_blight",
        "Tomato___Late_blight",         "Tomato___Leaf_Mold",
        "Tomato___Septoria_leaf_spot",  "Tomato___Spider_mites",
        "Tomato___Target_Spot",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "Tomato___Tomato_mosaic_virus", "Tomato___healthy",
    ]

    # ── Recommendations per disease ───────────────────────────────────────────
    DISEASE_RECOMMENDATIONS = {
        "healthy":                    "✅ Crop is healthy! Continue regular monitoring and good agricultural practices.",
        "Apple___Apple_scab":         "🍎 Apply captan or mancozeb fungicide. Remove infected leaves. Ensure air circulation.",
        "Apple___Black_rot":          "🍎 Prune infected branches. Apply copper-based fungicide. Remove mummified fruits.",
        "Apple___Cedar_apple_rust":   "🍎 Apply myclobutanil or mancozeb. Remove nearby juniper/cedar trees if possible.",
        "Cherry___Powdery_mildew":    "🍒 Apply sulfur-based fungicide. Improve air circulation. Avoid overhead irrigation.",
        "Corn___Cercospora_leaf_spot":"🌽 Use resistant varieties. Apply azoxystrobin or pyraclostrobin fungicide.",
        "Corn___Common_rust":         "🌽 Apply triazole fungicides. Plant resistant hybrid varieties.",
        "Corn___Northern_Leaf_Blight":"🌽 Apply propiconazole or azoxystrobin. Use disease-resistant varieties.",
        "Grape___Black_rot":          "🍇 Apply mancozeb or myclobutanil. Remove infected berries and leaves immediately.",
        "Grape___Esca_Black_Measles": "🍇 No effective cure. Remove infected wood. Apply fungicide preventively.",
        "Grape___Leaf_blight":        "🍇 Apply copper-based fungicide. Improve canopy air flow.",
        "Orange___Haunglongbing":     "🍊 No cure available. Remove infected trees. Control psyllid vectors.",
        "Peach___Bacterial_spot":     "🍑 Apply copper bactericide. Use disease-resistant peach varieties.",
        "Pepper___Bacterial_spot":    "🌶️ Apply copper bactericide. Avoid overhead irrigation. Remove infected plants.",
        "Potato___Early_blight":      "🥔 Apply chlorothalonil or mancozeb. Ensure adequate nutrition. Remove infected leaves.",
        "Potato___Late_blight":       "🥔 Apply metalaxyl IMMEDIATELY. This spreads fast — destroy heavily infected plants.",
        "Squash___Powdery_mildew":    "🟡 Apply sulfur or potassium bicarbonate. Improve spacing for air flow.",
        "Strawberry___Leaf_scorch":   "🍓 Apply captan fungicide. Remove infected leaves. Avoid wetting foliage.",
        "Tomato___Bacterial_spot":    "🍅 Apply copper-based bactericide. Avoid working in wet conditions.",
        "Tomato___Early_blight":      "🍅 Apply chlorothalonil fungicide. Mulch soil surface. Avoid wetting foliage.",
        "Tomato___Late_blight":       "🍅 Apply mancozeb or metalaxyl immediately. Spreads very fast — act urgently.",
        "Tomato___Leaf_Mold":         "🍅 Improve greenhouse ventilation. Apply copper fungicide. Remove infected leaves.",
        "Tomato___Septoria_leaf_spot":"🍅 Apply fungicides at first sign. Remove infected leaves. Practice crop rotation.",
        "Tomato___Spider_mites":      "🍅 Apply miticide or neem oil. Increase humidity. Remove heavily infested leaves.",
        "Tomato___Target_Spot":       "🍅 Apply azoxystrobin fungicide. Remove infected leaves. Ensure good air flow.",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "🍅 Control whitefly vectors. Use resistant varieties. Remove infected plants.",
        "Tomato___Tomato_mosaic_virus": "🍅 No cure. Remove infected plants. Disinfect tools. Control aphid vectors.",
    }
