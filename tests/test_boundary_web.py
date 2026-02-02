# tests/test_boundary_web.py
from __future__ import annotations  # R-T0: 将来アノテーション対応

import pytest  # R-T0: pytest を使う

from app import create_app  # R-T1: Flaskアプリを作るために使う


@pytest.fixture()
def client():  # R-T1: テスト用クライアントを作る
    app = create_app()  # R-T1: アプリ生成
    app.config.update(TESTING=True)  # R-T1: テストモード
    return app.test_client()  # R-T1: HTTPクライアントを返す


def test_get_boundary_ok(client):  # S-T1: GET /boundary は 200
    r = client.get("/boundary")  # S-T1: 画面を開く
    assert r.status_code == 200  # S-T1: 200であること
    text = r.get_data(as_text=True)  # S-T3: HTML本文を文字列化
    assert ("境界テンプレ" in text) or ("boundary" in text)  # S-T3: 画面っぽい文言がある


def test_post_boundary_ok(client):  # S-T2: POST /boundary は 200
    data = {  # S-T2: 必須4項目を送る
        "threat": "1",  # S-T2: 数値はフォームなので文字列でOK
        "body_alarm": "1",  # S-T2
        "need_clarity": "2",  # S-T2
        "energy": "1",  # S-T2
    }
    r = client.post("/boundary", data=data)  # S-T2: フォーム送信
    assert r.status_code == 200  # S-T2: 200であること
    text = r.get_data(as_text=True)  # S-T3: HTML本文を文字列化
    assert ("結果" in text) or ("推奨方策" in text)  # S-T3: 結果画面っぽい文言がある