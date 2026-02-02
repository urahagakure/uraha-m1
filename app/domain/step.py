from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List

from app.domain.contracts import StepInput

@dataclass(frozen=True)
class StepOutput:
    pi_t: str
    o_t1_pred: Dict[str, Any]
    notes: List[str]

def simulate_step(x: StepInput) -> StepOutput:
    # V0: いままでの挙動を最低限で再現（後で差し替え可能）
    threat = int(x.o_t.get("threat", 0))
    body_alarm = int(x.o_t.get("body_alarm", 0))
    need_clarity = int(x.o_t.get("need_clarity", 0))
    energy = int(x.o_t.get("energy", 0))

    if threat >= 2 or body_alarm >= 2:
        pi = "withdraw"
        notes = ["安全優先：距離を取り、状況を落ち着かせるのが良さそうです。"]
    else:
        pi = "engage"
        notes = ["対話優先：落ち着いて状況確認できそうです。"]

    o_pred = {
        "threat": max(0, threat - 1),
        "body_alarm": max(0, body_alarm - 1),
        "need_clarity": need_clarity,
        "energy": energy,
    }
    return StepOutput(pi_t=pi, o_t1_pred=o_pred, notes=notes)