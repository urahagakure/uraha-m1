from __future__ import annotations  # R8-0: 前方参照を安定させる

from flask import Blueprint, render_template, request  # R8-1: ルート/テンプレ/入力を扱う

from app.core.contracts import StepInput  # R8-2: 契約型で入力を組み立てる
from app.core.simulator import simulate_step  # R8-3: 1-stepを回す
from app.storage.repository import init_db, save_step, read_step  # R8-4: 保存と「過去ログ読み取り」に使う

from app.validators import validate_boundary_form  # R15-6: 定義準拠の検証を使う

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


@bp_boundary.get("/boundary")  # R10-0: 入力フォームを表示する
def boundary_form():
    # R10-1: クエリから直接フォーム値を受け取れるようにする（結果→再実行用）
    q_threat = request.args.get("threat")  # R10-1: threatをクエリから受け取る
    q_body_alarm = request.args.get("body_alarm")  # R10-1: body_alarmをクエリから受け取る
    q_need_clarity = request.args.get("need_clarity")  # R10-1: need_clarityをクエリから受け取る
    q_energy = request.args.get("energy")  # R10-1: energyをクエリから受け取る

    form = {"threat": "0", "body_alarm": "0", "need_clarity": "0", "energy": "0"}  # R10-2: デフォルト初期値

    # R10-3: クエリ値が揃っているなら、それを優先してフォームを作る
    if any(v is not None for v in (q_threat, q_body_alarm, q_need_clarity, q_energy)):  # R10-3: どれかが来ていれば
        form = {  # R10-3: クエリ値を文字列のままフォームに入れる（入力保持と同じ方針）
            "threat": q_threat or "0",  # R10-3: threat
            "body_alarm": q_body_alarm or "0",  # R10-3: body_alarm
            "need_clarity": q_need_clarity or "0",  # R10-3: need_clarity
            "energy": q_energy or "0",  # R10-3: energy
        }
        return render_template("boundary_form.html", form=form, error=None)  # R10-3: クエリフォームで描画する

    # R10-4: クエリが無い場合は step_id を見る（従来の再実行）
    step_id = request.args.get("step_id")  # R10-4: 再実行元ログID（任意）
    if step_id:  # R10-4: step_idが指定されている場合
        step = read_step(_to_int(step_id, 0))  # R10-4: DBからログを読む
        if step and isinstance(step.get("o_t"), dict):  # R10-4: o_tが辞書なら
            form = _build_form_from_ot(step["o_t"])  # R10-4: o_tからフォームを作る

    return render_template("boundary_form.html", form=form, error=None)  # R10-2: デフォルト/step_idで描画する

@bp_boundary.post("/boundary")  # R5-2: フォーム送信を処理する
def boundary_submit():
    # --- 1) 入力検証（ここはあなたの現行実装に合わせてOK） ---
    # 例: threat/body_alarm/... を作る or validate_boundary_form を使う

    cleaned, err = validate_boundary_form(request.form)  # R15-6: 検証+正規化
    if err:
        return render_template("boundary_form.html", error=err, form=dict(request.form)), 400  # R15-err-1: テンプレで安定参照

    threat = cleaned["threat"]  # R15-6
    body_alarm = cleaned["body_alarm"]  # R15-6
    need_clarity = cleaned["need_clarity"]  # R15-6
    energy = cleaned["energy"]  # R15-6

    # --- 2) s_t / o_t を構成（あなたの現行そのままでOK） ---
    s_t = {"energy": energy}  # R5-7: 隠れ状態（V0では最小）
    o_t = {  # R5-7: 観測
        "threat": threat,
        "body_alarm": body_alarm,
        "need_clarity": need_clarity,
        "energy": energy,
    }

    # --- 3) StepInputを作る（ここが 94行目付近のはず） ---
    x = StepInput(  # R8-4: 契約どおりにStepInputを作る
        s_t=s_t,  # R8-4
        o_t=o_t,  # R8-4
        prefs={"safe": 0.7, "connect": 0.3},  # R8-4: 好み（V0固定）
        precision={"policy": 1.0},  # R8-4: 精度（V0固定）
    )

    # --- 4) 1-stepシミュレート ---
    y = simulate_step(x)  # R8-5: 1-step回す

    # --- 5) 保存 ---
    init_db()  # R8-6: スキーマ初期化（冪等）
    row_id = save_step(  # R8-6: 1行保存
        template_id="boundary",
        s_t=s_t,
        o_t=o_t,
        pi_t=y.pi_t,
        o_t1_pred=y.o_t1_pred,
        notes=y.notes,
    )

    # --- 6) 結果ページ ---
    return render_template(  # R5-2: 結果ページを返す
        "boundary_result.html",
        row_id=row_id,
        s_t=s_t,
        o_t=o_t,
        pi_t=y.pi_t,
        o_t1_pred=y.o_t1_pred,
        notes=y.notes,
    )