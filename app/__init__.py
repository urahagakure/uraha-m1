from __future__ import annotations

from flask import Flask, redirect, render_template, request, url_for

from app.config import Config
from app.models import Issue, db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def home():
        return render_template("home.html")

    @app.get("/issues")
    def issues_index():
        issues = Issue.query.order_by(Issue.created_at.desc()).all()
        return render_template("issues/index.html", issues=issues)

    @app.route("/issues/new", methods=["GET", "POST"])
    def issues_new():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            tags = request.form.get("tags", "").strip()
            note = request.form.get("note", "").strip()
            intensity_raw = request.form.get("intensity", "0").strip()
            errors: list[str] = []

            try:
                intensity = int(intensity_raw)
            except ValueError:
                intensity = 0
                errors.append("Intensity must be a number.")

            if not 0 <= intensity <= 10:
                errors.append("Intensity must be between 0 and 10.")

            if not title:
                errors.append("Title is required.")

            if errors:
                return (
                    render_template(
                        "issues/new.html",
                        errors=errors,
                        form={
                            "title": title,
                            "tags": tags,
                            "note": note,
                            "intensity": intensity_raw,
                        },
                    ),
                    400,
                )

            issue = Issue(title=title, tags=tags, intensity=intensity, note=note)
            db.session.add(issue)
            db.session.commit()
            return redirect(url_for("issues_index"))

        return render_template("issues/new.html", errors=[], form={})

    return app
