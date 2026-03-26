from flask import Flask
from web.routes import web

import threading
from main import run_system

app = Flask(__name__)
app.register_blueprint(web)

# =========================
# START AI SYSTEM THREAD
# =========================
threading.Thread(target=run_system, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)