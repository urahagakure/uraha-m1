from __future__ import annotations

import os
from app import create_app  # app/__init__.py の create_app を読む

app = create_app()

if __name__ == "__main__":
    host = os.getenv("URAHAM1_HOST", "127.0.0.1")
    port = int(os.getenv("URAHAM1_PORT", "5001"))
    debug = os.getenv("URAHAM1_DEBUG", "1") == "1"

    # 重要：reloader を切る（2プロセス起動やcwd事故を避ける）
    app.run(host=host, port=port, debug=debug, use_reloader=False)