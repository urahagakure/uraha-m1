# app/templates_def/registry.py
from __future__ import annotations  # R-TPL2: 既存互換（型）を崩さない

from dataclasses import dataclass  # R-TPL1: テンプレ定義をデータとして束ねる
from typing import Callable, Dict, List  # R-TPL1: registry の型を明確化

from app.templates_def.boundary import BOUNDARY_FIELDS, FieldDef, boundary_defaults  # R-TPL3: 入口を一本化


@dataclass(frozen=True)  # R-TPL1: テンプレ定義は不変として扱う
class TemplateDef:  # R-TPL1: テンプレ定義の最小契約
    template_id: str  # R-TPL3: テンプレID（例: "boundary"）
    fields: List[FieldDef]  # R-TPL1: 入力定義
    defaults: Callable[[], Dict[str, int]]  # R-TPL2: デフォルト生成（関数で持つ）


# R-TPL3: ここが「追加テンプレの唯一の入口」
TEMPLATES: Dict[str, TemplateDef] = {  # R-TPL3: registry 本体
    "boundary": TemplateDef(  # R-TPL3: boundary を登録
        template_id="boundary",  # R-TPL3
        fields=BOUNDARY_FIELDS,  # R-TPL1
        defaults=boundary_defaults,  # R-TPL2
    )
}


def get_template(template_id: str) -> TemplateDef:  # R-TPL3: 参照API
    t = TEMPLATES.get(template_id)  # R-TPL3: registry から取得
    if t is None:  # R-TPL3: 未登録を明示的にエラーにする
        raise KeyError(f"Unknown template_id: {template_id}")  # R-TPL3
    return t  # R-TPL3