from __future__ import annotations  # R-run-0: 型注釈の前方参照を安定させる

from app import create_app  # R-run-1: create_app からFlaskアプリを生成する

app = create_app()  # R-run-2: アプリを生成する（Blueprint登録もここで反映される）

if __name__ == "__main__":  # R-run-3: 直叩き実行時だけサーバを起動する
    app.run(host="0.0.0.0", port=5001, debug=True)  # R-run-4: 5000衝突回避のため5001で起動する