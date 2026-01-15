from __future__ import annotations  # R15-0: 型注釈を安定させる

from dataclasses import dataclass  # R15-1: 定義をデータとして持つ
from typing import List, Dict  # R15-1: 返却型を明示する


@dataclass(frozen=True)  # R15-2: 定義は不変（書き換え事故防止）
class FieldDef:
    key: str  # R15-4: 入力キー（name属性）
    label: str  # R15-4: 表示名
    min: int  # R15-4: 最小値
    max: int  # R15-4: 最大値
    step: int  # R15-4: ステップ
    default: int  # R15-4: 既定値


BOUNDARY_FIELDS: List[FieldDef] = [  # R15-3: boundaryテンプレの入力定義
    FieldDef(key="threat", label="脅威推定 threat (0-3)", min=0, max=3, step=1, default=0),  # R15-3
    FieldDef(key="body_alarm", label="身体警報 body_alarm (0-3)", min=0, max=3, step=1, default=0),  # R15-3
    FieldDef(key="need_clarity", label="ニーズ明確度 need_clarity (0-3)", min=0, max=3, step=1, default=0),  # R15-3
    FieldDef(key="energy", label="余力 energy (0-3)", min=0, max=3, step=1, default=0),  # R15-3
]  # R15-3


def boundary_defaults() -> Dict[str, int]:  # R15-4: 既定値辞書を返す
    return {f.key: f.default for f in BOUNDARY_FIELDS}  # R15-4: key→default