from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def append_event(event: Dict[str, Any], *, path: Path) -> Path:
    """
    JSONL(1行1JSON) に追記して保存先Pathを返す。
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # 最低限の保険：ts が無ければ入れる
    if "ts" not in event:
        event["ts"] = datetime.now(timezone.utc).isoformat()

    line = json.dumps(event, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

    return path