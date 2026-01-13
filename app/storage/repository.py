from __future__ import annotations  # R4-3: 前方参照を安定させる

import json  # R4-1: dict/listをJSON文字列にする
from datetime import datetime, timezone  # R4-1: created_at をUTCで統一する
from typing import Any, Dict, List, Mapping  # R4-2: 最小型を明示する

from app.storage.db import connect, init_schema  # R4-1: DB接続とスキーマ初期化を使う


def init_db() -> None:  # R4-1: 外から呼べる初期化関数
    conn = connect()  # R4-4: instance/app.db に接続する
    try:  # R4-3: 例外が起きても接続を閉じる
        init_schema(conn)  # R4-1: テーブルを作る
    finally:  # R4-3: 必ず閉じる
        conn.close()  # R4-3: 接続を閉じる


def save_step(  # R4-1: 1-stepログを保存する
    template_id: str,  # R4-2: 例: "boundary"
    s_t: Mapping[str, Any],  # R4-2: 隠れ状態（入力）
    o_t: Mapping[str, Any],  # R4-2: 観測（入力）
    pi_t: str,  # R4-2: 方策ID
    o_t1_pred: Mapping[str, Any],  # R4-2: 予測観測（出力）
    notes: List[str],  # R4-2: 介入案（出力）
) -> int:
    created_at = datetime.now(timezone.utc).isoformat()  # R4-1: UTCのISO時刻を作る

    conn = connect()  # R4-4: DBへ接続する
    try:  # R4-3: 例外が起きても接続を閉じる
        init_schema(conn)  # R4-1: 念のためスキーマを確保する（冪等）
        cur = conn.execute(  # R4-1: 1行挿入する
            """
            INSERT INTO steps (created_at, template_id, s_t_json, o_t_json, pi_t, o_t1_pred_json, notes_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,  # R4-1: created_at
                template_id,  # R4-2: template_id
                json.dumps(dict(s_t), ensure_ascii=False),  # R4-1: s_t をJSON化
                json.dumps(dict(o_t), ensure_ascii=False),  # R4-1: o_t をJSON化
                pi_t,  # R4-2: pi_t
                json.dumps(dict(o_t1_pred), ensure_ascii=False),  # R4-1: 予測をJSON化
                json.dumps(list(notes), ensure_ascii=False),  # R4-1: notesをJSON化
            ),
        )
        conn.commit()  # R4-1: 変更を確定する
        return int(cur.lastrowid)  # R4-1: 保存した行IDを返す
    finally:  # R4-3: 必ず閉じる
        conn.close()  # R4-3: 接続を閉じる

import json  # R6-3: JSON文字列をdict/listに戻す
from typing import Any, Dict, List, Optional  # R6-1: 返却型を明示する

from app.storage.db import connect, init_schema  # R6-1: DB接続とスキーマ確保を再利用する


def _loads_json(s: str, default: Any) -> Any:  # R6-3: JSON復元を安全に行う（壊れた値でも落とさない）
    try:  # R6-3: json.loadsで復元を試す
        return json.loads(s)  # R6-3: 復元できた値を返す
    except Exception:  # R6-3: 失敗したら
        return default  # R6-3: デフォルトを返す


def list_steps(limit: int = 50) -> List[Dict[str, Any]]:  # R6-1: 最新N件のstep履歴を返す
    conn = connect()  # R6-1: instance/app.dbへ接続する
    try:  # R6-1: 必ずcloseするためtry/finallyにする
        init_schema(conn)  # R6-1: stepsテーブルが無い環境でも落ちないよう確保する（冪等）
        cur = conn.execute(  # R6-1: 最新順にN件取得する
            """
            SELECT id, created_at, template_id, s_t_json, o_t_json, pi_t, o_t1_pred_json, notes_json
            FROM steps
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(limit),),  # R6-1: LIMITは整数にして渡す
        )
        rows = cur.fetchall()  # R6-1: 行を全件取得する
        out: List[Dict[str, Any]] = []  # R6-1: 返却リストを用意する
        for r in rows:  # R6-1: 各行を辞書に整形する
            out.append(  # R6-1: 1行分の辞書を追加する
                {
                    "id": int(r["id"]),  # R6-1: id
                    "created_at": r["created_at"],  # R6-1: created_at
                    "template_id": r["template_id"],  # R6-1: template_id
                    "s_t": _loads_json(r["s_t_json"], {}),  # R6-3: s_t_json → dict
                    "o_t": _loads_json(r["o_t_json"], {}),  # R6-3: o_t_json → dict
                    "pi_t": r["pi_t"],  # R6-1: pi_t
                    "o_t1_pred": _loads_json(r["o_t1_pred_json"], {}),  # R6-3: o_t1_pred_json → dict
                    "notes": _loads_json(r["notes_json"], []),  # R6-3: notes_json → list
                }
            )
        return out  # R6-1: 整形済みリストを返す
    finally:  # R6-1: 必ず閉じる
        conn.close()  # R6-1: DB接続を閉じる


def read_step(step_id: int) -> Optional[Dict[str, Any]]:  # R6-2: id指定で1件返す（無ければNone）
    conn = connect()  # R6-2: instance/app.dbへ接続する
    try:  # R6-2: 必ずcloseするためtry/finallyにする
        init_schema(conn)  # R6-2: stepsテーブルが無い環境でも落ちないよう確保する（冪等）
        cur = conn.execute(  # R6-2: idで1件取得する
            """
            SELECT id, created_at, template_id, s_t_json, o_t_json, pi_t, o_t1_pred_json, notes_json
            FROM steps
            WHERE id = ?
            """,
            (int(step_id),),  # R6-2: idは整数にして渡す
        )
        r = cur.fetchone()  # R6-2: 1行取得する
        if r is None:  # R6-2: 見つからない場合
            return None  # R6-2: Noneを返す
        return {  # R6-2: 見つかった行を辞書に整形して返す
            "id": int(r["id"]),  # R6-2: id
            "created_at": r["created_at"],  # R6-2: created_at
            "template_id": r["template_id"],  # R6-2: template_id
            "s_t": _loads_json(r["s_t_json"], {}),  # R6-3: s_t_json → dict
            "o_t": _loads_json(r["o_t_json"], {}),  # R6-3: o_t_json → dict
            "pi_t": r["pi_t"],  # R6-2: pi_t
            "o_t1_pred": _loads_json(r["o_t1_pred_json"], {}),  # R6-3: o_t1_pred_json → dict
            "notes": _loads_json(r["notes_json"], []),  # R6-3: notes_json → list
        }
    finally:  # R6-2: 必ず閉じる
        conn.close()  # R6-2: DB接続を閉じる