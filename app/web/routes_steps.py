from __future__ import annotations  # R7-0: 型注釈の前方参照を安定させる

from flask import Blueprint, abort, render_template, request  # R7-1: ルート定義とテンプレ表示を行う

from app.storage.repository import list_steps, read_step  # R7-1: 履歴取得APIを呼ぶ


bp_steps = Blueprint("steps", __name__)  # R7-1: 履歴画面専用のBlueprint


@bp_steps.get("/steps")  # R7-1: 履歴一覧を表示する
def steps_index():
    limit = int(request.args.get("limit", "50"))  # R7-1: ?limit= で表示件数を変えられる
    steps = list_steps(limit=limit)  # R7-1: 最新N件を取得する
    return render_template("steps/index.html", steps=steps, limit=limit)  # R7-1: 一覧テンプレを返す


@bp_steps.get("/steps/<int:step_id>")  # R7-2: 履歴詳細を表示する
def steps_show(step_id: int):
    step = read_step(step_id)  # R7-2: id指定で1件取得する
    if step is None:  # R7-2: 無ければ
        abort(404)  # R7-2: 404にする
    return render_template("steps/show.html", step=step)  # R7-2: 詳細テンプレを返す