from __future__ import annotations  # R4-3: 前方参照を安定させる

import sqlite3  # R4-4: SQLiteに接続する
from pathlib import Path  # R4-4: instance/app.db のパスを安全に扱う


def get_db_path() -> Path:  # R4-4: DBファイルの場所を一箇所に固定する
    return Path("instance") / "app.db"  # R4-4: 既存運用（instance/app.db）に合わせる


def connect() -> sqlite3.Connection:  # R4-3: 使い回せる接続を返す
    db_path = get_db_path()  # R4-4: DBパスを取得する
    db_path.parent.mkdir(parents=True, exist_ok=True)  # R4-4: instance/ が無ければ作る
    conn = sqlite3.connect(str(db_path))  # R4-4: SQLiteへ接続する
    conn.row_factory = sqlite3.Row  # R4-3: 取得結果を辞書風に扱えるようにする
    return conn  # R4-3: Connectionを返す


def init_schema(conn: sqlite3.Connection) -> None:  # R4-1: 必要テーブルを作成する
    conn.execute(  # R4-1: stepsテーブルを作る
        """
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            template_id TEXT NOT NULL,
            s_t_json TEXT NOT NULL,
            o_t_json TEXT NOT NULL,
            pi_t TEXT NOT NULL,
            o_t1_pred_json TEXT NOT NULL,
            notes_json TEXT NOT NULL
        )
        """
    )
    conn.commit()  # R4-1: 変更を確定する