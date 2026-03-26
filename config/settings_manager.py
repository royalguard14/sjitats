import json
import os

SETTINGS_FILE = "config/settings.json"

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

    "TELEGRAM_TOKEN": "8420251258:AAHV8FewCqen5EIgIVUklYnYIdNQZbiJjLk",
    "TELEGRAM_CHAT_ID": "5303681167"
}


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings)
        return default_settings

    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)


def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def update_settings(new_data):
    settings = load_settings()
    settings.update(new_data)
    save_settings(settings)
    return settings