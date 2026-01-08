from flask import Flask, render_template

from app.config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.get("/")
    def home():
        return render_template("home.html")

    return app
