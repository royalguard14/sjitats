from flask import Flask
from web.routes import web
from main import start_system

app = Flask(__name__)
app.register_blueprint(web)

# Start the security system in background
start_system()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
