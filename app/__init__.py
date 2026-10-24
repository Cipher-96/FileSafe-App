import os
from flask import Flask
from dotenv import load_dotenv

from app.security import apply_security_headers
from app.routes import register_routes
from app.config import Config


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)
    os.makedirs(app.config["TEMP_FOLDER"], exist_ok=True)

    @app.after_request
    def add_security_headers(response):
        return apply_security_headers(response)

    register_routes(app)
    return app
