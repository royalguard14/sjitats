import requests
import cv2

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, message):
        try:
            url = f"{self.base_url}/sendMessage"
            data = {"chat_id": self.chat_id, "text": message}
            requests.post(url, data=data)
        except Exception as e:
            print("❌ Telegram message error:", e)

    def send_image(self, frame, caption="Alert"):
        try:
            _, img_encoded = cv2.imencode('.jpg', frame)

            url = f"{self.base_url}/sendPhoto"

            files = {
                "photo": ("image.jpg", img_encoded.tobytes())
            }

            data = {
                "chat_id": self.chat_id,
                "caption": caption
            }

            requests.post(url, files=files, data=data)

        except Exception as e:
            print("❌ Telegram image error:", e)