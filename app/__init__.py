from __future__ import annotations

from pathlib import Path

from flask import Flask

from app.config import Config
from app.models import Issue, db

def create_app() -> Flask:
    app = Flask(__name__)

    app.config.from_object(Config)

    # EVENT_LOG_PATH は config 由来でも絶対パスに正規化して固定する
    project_root = Path(__file__).resolve().parent.parent
    default_log_path = project_root / "instance" / "events.jsonl"
    configured_log_path = app.config.get("EVENT_LOG_PATH") or default_log_path
    log_path = Path(configured_log_path).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    app.config["EVENT_LOG_PATH"] = log_path

    db.init_app(app)

    with app.app_context():
        db.create_all()  # ★ これが無いとDB系が初回で事故りやすい

    # ★ Blueprint を戻す（boundary / steps を生やす）
    from app.web.routes_boundary import bp_boundary
    app.register_blueprint(bp_boundary)

    from app.web.routes_steps import bp_steps
    app.register_blueprint(bp_steps)

    return app


