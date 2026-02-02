from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True)
class StepInput:
    s_t: Dict[str, Any]
    o_t: Dict[str, Any]
    prefs: Dict[str, Any]
    precision: Dict[str, Any]