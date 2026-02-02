from __future__ import annotations  # R1

from datetime import datetime, timezone  # R2
from pathlib import Path  # R3
from typing import Any, Dict, Tuple  # R4

from flask import Blueprint, current_app, jsonify, render_template, request  # R5

from app.domain.contracts import StepInput
from app.domain.step import simulate_step
from app.infra.jsonl import append_event
from app.templates_def.boundary import boundary_defaults

bp_boundary = Blueprint("boundary", __name__)  # R9


def _validate(form: Dict[str, Any]) -> Tuple[Dict[str, Any], str | None]:  # R10
    def _i(name: str, lo: int, hi: int, default: int) -> int:  # R11
        try:
            v = int(form.get(name, default))
        except Exception:
            return default
        return max(lo, min(hi, v))

    def _f(name: str, lo: float, hi: float, default: float) -> float:  # R12
        try:
            v = float(form.get(name, default))
        except Exception:
            return default
        return max(lo, min(hi, v))

    cleaned = {
        "threat": _i("threat", 0, 3, 2),
        "body_alarm": _i("body_alarm", 0, 3, 2),
        "need_clarity": _i("need_clarity", 0, 3, 1),
        "energy": _i("energy", 0, 3, 2),
        "safe": _f("safe", 0.0, 1.0, 0.7),
        "connect": _f("connect", 0.0, 1.0, 0.3),
        "prec_policy": _f("prec_policy", 0.0, 3.0, 1.0),
    }
    return cleaned, None


def _build_step_input(cleaned: Dict[str, Any]) -> StepInput:  # R20
    x = StepInput(
        s_t={"energy": int(cleaned["energy"])},
        o_t={
            "threat": int(cleaned["threat"]),
            "body_alarm": int(cleaned["body_alarm"]),
            "need_clarity": int(cleaned["need_clarity"]),
            "energy": int(cleaned["energy"]),
        },
        prefs={"safe": float(cleaned["safe"]), "connect": float(cleaned["connect"])},
        precision={"policy": float(cleaned["prec_policy"])},
    )
    return x


def _save_event(*, x: StepInput, y) -> Path:
    event = {
        "ok": True,  # ★追加：成功フラグ（将来の失敗ログと混ぜても判別できる）
        "app": "uraha_m1_flask",
        "template": "boundary_v0",
        "ts": datetime.now(timezone.utc).isoformat(),

        "source": "m1_flask",        # ★追加：どの実行元か（m2/m3/m4と揃える）
        "route": request.path,       # ★追加：/boundary or /api/boundary
        "endpoint": request.endpoint,# ★追加：boundary.boundary_submit_api みたいな識別子
        "method": request.method,    # ★追加：POST/GET

        "input": {
            "s_t": x.s_t,
            "o_t": x.o_t,
            "prefs": x.prefs,
            "precision": x.precision,
        },
        "output": {
            "pi_t": y.pi_t,
            "o_t1_pred": y.o_t1_pred,
            "notes": y.notes,
        },
    }

    log_path = current_app.config.get("EVENT_LOG_PATH")  # ★KeyError回避
    if not log_path:
        # 念のための保険（基本ここには来ない）
        project_root = Path(current_app.root_path).parent
        log_path = (project_root / "instance" / "events.jsonl").resolve()

    log_path = Path(log_path).resolve()  # 相対設定が来ても絶対化して固定
    current_app.config["EVENT_LOG_PATH"] = log_path  # 次回以降も安定
    log_path.parent.mkdir(parents=True, exist_ok=True)  # ★ここで必ず作る
    saved_to = append_event(event, path=log_path)
    return saved_to

def _run(cleaned: Dict[str, Any]):
    x = StepInput(
        s_t={"energy": int(cleaned["energy"])},
        o_t={
            "threat": int(cleaned["threat"]),
            "body_alarm": int(cleaned["body_alarm"]),
            "need_clarity": int(cleaned["need_clarity"]),
            "energy": int(cleaned["energy"]),
        },
        prefs={"safe": float(cleaned["safe"]), "connect": float(cleaned["connect"])},
        precision={"policy": float(cleaned["prec_policy"])},
    )
    y = simulate_step(x)
    return x, y


@bp_boundary.get("/boundary")
def boundary_form():
    defaults = boundary_defaults()
    return render_template("boundary_form.html", form=defaults, error=None), 200


@bp_boundary.post("/boundary")
def boundary_submit_html():
    cleaned, err = _validate(request.form)
    if err:
        return render_template("boundary_form.html", form=cleaned, error=err), 400

    x, y = _run(cleaned)
    saved_to = _save_event(x=x, y=y)
    return render_template("boundary_result.html", y=y, saved_to=str(saved_to)), 200


@bp_boundary.post("/api/boundary")
def boundary_submit_api():
    payload = request.get_json(silent=True) or {}
    cleaned, err = _validate(payload)
    if err:
        body = {
            "ok": False,
            "error": err,
            "input": cleaned,
        }
        # DEBUG時だけ付ける（推奨）
        if current_app.debug:
            body["log_path_abs"] = str(current_app.config["EVENT_LOG_PATH"])
            body["cwd"] = str(Path.cwd())
        return jsonify(body), 400

    x, y = _run(cleaned)
    saved_to = _save_event(x=x, y=y)  # saved_to は Path の想定

    body = {
        "ok": True,
        "saved_to": str(saved_to.resolve()),  # ★絶対パスで固定（1本で十分）
        "pi_t": y.pi_t,
        "o_t1_pred": y.o_t1_pred,
        "notes": y.notes,
    }

    if current_app.debug:
        body["log_path_abs"] = str(Path(current_app.config["EVENT_LOG_PATH"]).resolve())
        body["cwd"] = str(Path.cwd())

    return jsonify(body), 200


