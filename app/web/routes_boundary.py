from __future__ import annotations  # R5-1: 型注釈の前方参照を安定させる

from flask import Blueprint, render_template, request  # R5-2: ルート定義とフォーム入力を扱う

from app.core.contracts import StepInput  # R5-3: 契約型で1-step入力を作る
from app.core.simulator import simulate_step  # R5-4: ダミー1-stepを呼ぶ
from app.storage.repository import init_db, save_step  # R5-5: DB初期化と保存を呼ぶ


bp_boundary = Blueprint("boundary", __name__)  # R5-2: 境界テンプレ専用のBlueprint


@bp_boundary.get("/boundary")  # R5-2: 入力フォームを表示する
def boundary_form():
    return render_template("boundary_form.html")  # R5-2: テンプレを返す


@bp_boundary.post("/boundary")  # R5-2: フォーム送信を処理する
def boundary_submit():
    # R5-6: フォーム入力を整数として受け取る（無ければ0）
    threat = int(request.form.get("threat", "0"))  # R5-6: 脅威推定
    body_alarm = int(request.form.get("body_alarm", "0"))  # R5-6: 身体警報
    need_clarity = int(request.form.get("need_clarity", "0"))  # R5-6: ニーズ明確度
    energy = int(request.form.get("energy", "0"))  # R5-6: 余力

    s_t = {"energy": energy}  # R5-7: 隠れ状態（V0では最小でよい）
    o_t = {  # R5-7: 観測（V0では最小でよい）
        "threat": threat,
        "body_alarm": body_alarm,
        "need_clarity": need_clarity,
        "energy": energy,
    }

    x = StepInput(  # R5-3: 契約どおりに1-step入力を作る
        s_t=s_t,
        o_t=o_t,
        prefs={"safe": 0.7, "connect": 0.3},  # R5-8: 好み（V0は固定でよい）
        precision={"policy": 1.0},  # R5-8: 精度（V0は固定でよい）
    )

    y = simulate_step(x)  # R5-4: 1-stepを回す

    init_db()  # R5-5: 念のためスキーマ初期化（冪等）
    row_id = save_step(  # R5-5: 1行保存する
        template_id="boundary",
        s_t=s_t,
        o_t=o_t,
        pi_t=y.pi_t,
        o_t1_pred=y.o_t1_pred,
        notes=y.notes,
    )

    return render_template(  # R5-2: 結果ページを表示する
        "boundary_result.html",
        row_id=row_id,
        s_t=s_t,
        o_t=o_t,
        pi_t=y.pi_t,
        o_t1_pred=y.o_t1_pred,
        notes=y.notes,
    )