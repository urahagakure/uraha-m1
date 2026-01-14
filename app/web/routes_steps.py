from __future__ import annotations  # R7-0: 型注釈の前方参照を安定させる

from flask import Blueprint, abort, render_template, request  # R7-1: ルート定義とテンプレ表示を行う

from app.storage.repository import list_steps, read_step  # R7-1: 履歴取得APIを呼ぶ


bp_steps = Blueprint("steps", __name__)  # R7-1: 履歴画面専用のBlueprint


@bp_steps.get("/steps")  # R12-1: 履歴一覧を表示する
def steps_index():
    limit = int(request.args.get("limit", "50"))  # R12-1: 表示件数
    template = request.args.get("template")  # R12-2: template_idの絞り込み（任意）
    pi_t = request.args.get("pi_t")  # R12-3: 方策の絞り込み（任意）

    steps = list_steps(limit=limit)  # R12-1: まず最新N件を取得する（V0+はweb側で絞る）

    if template:  # R12-2: template指定があれば
        steps = [s for s in steps if s.get("template_id") == template]  # R12-2: template_idで絞る

    if pi_t:  # R12-3: pi_t指定があれば
        steps = [s for s in steps if s.get("pi_t") == pi_t]  # R12-3: pi_tで絞る

    count = len(steps)  # R13-2: フィルタ後の実件数を数える
    return render_template(  # R12-4: フィルタ条件もテンプレへ渡す
        "steps/index.html",  # R12-4: 一覧テンプレ
        steps=steps,  # R12-4: 表示対象のsteps
        limit=limit,  # R13-3: 取得上限（limit）
        template=template,  # R13-1: template（未指定ならNoneのまま渡す）
        pi_t=pi_t,  # R13-1: pi_t（未指定ならNoneのまま渡す）
        count=count,  # R13-2: 実件数をテンプレへ渡す
    )  # R12-4: 描画


@bp_steps.get("/steps/<int:step_id>")  # R7-2: 履歴詳細を表示する
def steps_show(step_id: int):
    step = read_step(step_id)  # R7-2: id指定で1件取得する
    if step is None:  # R7-2: 無ければ
        abort(404)  # R7-2: 404にする
    return render_template("steps/show.html", step=step)  # R7-2: 詳細テンプレを返す