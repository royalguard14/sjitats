import json
import os

# =========================
# SAFE FILE PATH
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# =========================
# DEFAULT SETTINGS
# =========================
default_settings = {
    "ENABLE_MOTION": True,
    "ENABLE_THERMAL": False,
    "ENABLE_FACE_RECOGNITION": True,

    "ENABLE_BUZZER": True,
    "ENABLE_LED": True,
    "ENABLE_NOTIFICATIONS": False,

    "MOTION_SENSITIVITY": 0.5,
    "FACE_RECOGNITION_THRESHOLD": 0.6,

    "CAMERA_RESOLUTION": [640, 480],

    "TELEGRAM_TOKEN": "",
    "TELEGRAM_CHAT_ID": "",

    # ✅ KNN SUPPORT
    "USE_KNN": False,
    "KNN_NEIGHBORS": 3
}

# =========================
# LOAD SETTINGS
# =========================
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings)
        return default_settings

    with open(SETTINGS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ settings.json corrupted. Resetting to default.")
            save_settings(default_settings)
            return default_settings

# =========================
# SAVE SETTINGS
# =========================
def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# UPDATE SETTINGS
# =========================
def update_settings(new_data):
    settings = load_settings()

    settings.update(new_data)

    save_settings(settings)

    return settings
