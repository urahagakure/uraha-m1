from __future__ import annotations  # R7-0: 型注釈の前方参照を安定させる

from flask import Blueprint, abort, render_template, request  # R7-1: ルート定義とテンプレ表示を行う

from app.storage.repository import list_steps_filtered, read_step  # R14-0: フィルタ版一覧と詳細取得


bp_steps = Blueprint("steps", __name__)  # R7-1: 履歴画面専用のBlueprint

@bp_steps.get("/steps")  # R14-0: 履歴一覧を表示する
def steps_index():
    limit = int(request.args.get("limit", "50"))  # R14-1: 取得上限
    template = request.args.get("template")  # R14-2: template絞り込み
    pi_t = request.args.get("pi_t")  # R14-3: pi_t絞り込み

    steps = list_steps_filtered(limit=limit, template=template, pi_t=pi_t)  # R14-4: DB側で絞り込む
    count = len(steps)  # R14-5: フィルタ後の実件数（必ず代入する）

    return render_template(  # R14-6: テンプレに渡す
        "steps/index.html",  # R14-6: 一覧テンプレ
        steps=steps,  # R14-6: 表示データ
        limit=limit,  # R14-6: 取得上限
        template=template,  # R14-6: template表示用
        pi_t=pi_t,  # R14-6: pi_t表示用
        count=count,  # R14-6: 実件数
    )  # R14-6: 描画


@bp_steps.get("/steps/<int:step_id>")  # R7-2: 履歴詳細を表示する
def steps_show(step_id: int):
    step = read_step(step_id)  # R7-2: id指定で1件取得する
    if step is None:  # R7-2: 無ければ
        abort(404)  # R7-2: 404にする
    return render_template("steps/show.html", step=step)  # R7-2: 詳細テンプレを返す