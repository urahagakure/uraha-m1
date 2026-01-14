from __future__ import annotations  # R8-0: 前方参照を安定させる

from flask import Blueprint, render_template, request  # R8-1: ルート/テンプレ/入力を扱う

from app.core.contracts import StepInput  # R8-2: 契約型で入力を組み立てる
from app.core.simulator import simulate_step  # R8-3: 1-stepを回す
from app.storage.repository import init_db, save_step, read_step  # R8-4: 保存と「過去ログ読み取り」に使う


bp_boundary = Blueprint("boundary", __name__)  # R8-1: 境界テンプレ用Blueprint


def _to_int(s: str, default: int = 0) -> int:  # R8-3: 文字列→intを安全に変換する
    try:  # R8-3: 変換を試す
        return int(s)  # R8-3: 変換できれば返す
    except (TypeError, ValueError):  # R8-3: 変換できなければ
        return default  # R8-3: defaultを返す


def _build_form_from_ot(o_t: dict) -> dict:  # R8-2: 過去ログのo_tからフォーム初期値を作る
    return {  # R8-2: フォームはテンプレで扱いやすいように文字列で持つ
        "threat": str(o_t.get("threat", 0)),  # R8-2: threat初期値
        "body_alarm": str(o_t.get("body_alarm", 0)),  # R8-2: body_alarm初期値
        "need_clarity": str(o_t.get("need_clarity", 0)),  # R8-2: need_clarity初期値
        "energy": str(o_t.get("energy", 0)),  # R8-2: energy初期値
    }  # R8-2: 必須項目を揃える


@bp_boundary.get("/boundary")  # R8-1: 入力フォームを表示する
def boundary_form():
    step_id = request.args.get("step_id")  # R8-2: 再実行元ログID（任意）を受け取る
    form = {"threat": "0", "body_alarm": "0", "need_clarity": "0", "energy": "0"}  # R8-2: デフォルト初期値

    if step_id:  # R8-2: step_idが指定されている場合
        step = read_step(_to_int(step_id, 0))  # R8-2: DBからログを読む（無ければNone）
        if step and isinstance(step.get("o_t"), dict):  # R8-2: o_tが辞書なら
            form = _build_form_from_ot(step["o_t"])  # R8-2: o_tからフォーム初期値を作る

    return render_template("boundary_form.html", form=form, error=None)  # R8-2: formを渡して描画する


@bp_boundary.post("/boundary")  # R8-1: フォーム送信を処理する
def boundary_submit():
    form = {  # R8-3: 再表示用に「そのままの入力」を保持する
        "threat": request.form.get("threat", "0"),  # R8-3: threat入力（文字列のまま保持）
        "body_alarm": request.form.get("body_alarm", "0"),  # R8-3: body_alarm入力（文字列のまま保持）
        "need_clarity": request.form.get("need_clarity", "0"),  # R8-3: need_clarity入力（文字列のまま保持）
        "energy": request.form.get("energy", "0"),  # R8-3: energy入力（文字列のまま保持）
    }  # R8-3: 入力保持が目的

    threat = _to_int(form["threat"], None)  # R8-3: int変換（失敗を検出したいのでdefault=None）
    body_alarm = _to_int(form["body_alarm"], None)  # R8-3: int変換
    need_clarity = _to_int(form["need_clarity"], None)  # R8-3: int変換
    energy = _to_int(form["energy"], None)  # R8-3: int変換

    if None in (threat, body_alarm, need_clarity, energy):  # R8-3: どれかが変換失敗なら
        return render_template("boundary_form.html", form=form, error="数値（0-3）で入力してください。"), 400  # R8-3: 入力保持で再表示
    if not (0 <= threat <= 3 and 0 <= body_alarm <= 3 and 0 <= need_clarity <= 3 and 0 <= energy <= 3):  # R9-1: 許容範囲（0〜3）を強制する
        return render_template("boundary_form.html", form=form, error="0〜3の範囲で入力してください。"), 400  # R9-2: 入力保持のまま400で再表示する
    s_t = {"energy": energy}  # R8-4: 隠れ状態（V0最小）
    o_t = {  # R8-4: 観測（V0最小）
        "threat": threat,  # R8-4: threat
        "body_alarm": body_alarm,  # R8-4: body_alarm
        "need_clarity": need_clarity,  # R8-4: need_clarity
        "energy": energy,  # R8-4: energy
    }  # R8-4: 入力を整形

    x = StepInput(  # R8-4: 契約どおりにStepInputを作る
        s_t=s_t,  # R8-4: 隠れ状態
        o_t=o_t,  # R8-4: 観測
        prefs={"safe": 0.7, "connect": 0.3},  # R8-4: 好み（V0固定）
        precision={"policy": 1.0},  # R8-4: 精度（V0固定）
    )  # R8-4: 1-step入力完成

    y = simulate_step(x)  # R8-5: 1-stepを回す

    init_db()  # R8-6: スキーマ確保（冪等）
    row_id = save_step(  # R8-6: ログ保存
        template_id="boundary",  # R8-6: template_id固定
        s_t=s_t,  # R8-6: 隠れ状態保存
        o_t=o_t,  # R8-6: 観測保存
        pi_t=y.pi_t,  # R8-6: 方策保存
        o_t1_pred=y.o_t1_pred,  # R8-6: 予測保存
        notes=y.notes,  # R8-6: 介入案保存
    )  # R8-6: 保存完了

    return render_template(  # R8-7: 結果表示
        "boundary_result.html",  # R8-7: 結果テンプレ
        row_id=row_id,  # R8-7: 保存ID表示
        s_t=s_t,  # R8-7: 入力表示
        o_t=o_t,  # R8-7: 入力表示
        pi_t=y.pi_t,  # R8-7: 方策表示
        o_t1_pred=y.o_t1_pred,  # R8-7: 予測表示
        notes=y.notes,  # R8-7: 介入案表示
    )  # R8-7: 描画