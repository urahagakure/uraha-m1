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