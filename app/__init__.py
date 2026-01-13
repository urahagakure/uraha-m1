from __future__ import annotations

from flask import Flask, redirect, render_template, request, url_for

from app.config import Config
from app.models import Issue, db
from app.validators import validate_issue_form


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
            data, errors = validate_issue_form(request.form)
            if errors:
                return (
                    render_template(
                        "issues/new.html",
                        errors=errors,
                        form=data,
                    ),
                    400,
                )

            issue = Issue(
                title=data["title"],
                tags=data["tags"],
                intensity=data["intensity"],
                note=data["note"],
            )
            db.session.add(issue)
            db.session.commit()
            return redirect(url_for("issues_index"))

        return render_template("issues/new.html", errors=[], form={})

    from app.web.routes_boundary import bp_boundary  # R5-2: 境界Blueprintを読み込む
    app.register_blueprint(bp_boundary)  # R5-2: /boundary ルートを有効化する
    from app.web.routes_steps import bp_steps  # R7-3: 履歴Blueprintを読み込む
    app.register_blueprint(bp_steps)  # R7-3: /steps を有効化する

    return app