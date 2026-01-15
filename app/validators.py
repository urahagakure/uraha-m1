from __future__ import annotations

from typing import Mapping, Tuple

from app.templates_def.boundary import BOUNDARY_FIELDS  # R15-6: 定義からrangeを取得する

def validate_issue_form(form: Mapping[str, str]) -> Tuple[dict, list[str]]:
    title = form.get("title", "").strip()
    tags = form.get("tags", "").strip()
    note = form.get("note", "").strip()
    intensity_raw = form.get("intensity", "0").strip()
    errors: list[str] = []

    try:
        intensity = int(intensity_raw)
    except ValueError:
        intensity = 0

    if not 0 <= intensity <= 10:
        errors.append("Intensity must be between 0 and 10.")

    if not title:
        errors.append("Title is required.")

    data = {
        "title": title,
        "tags": tags,
        "note": note,
        "intensity": intensity,
    }

    return data, errors

def validate_boundary_form(form: dict) -> tuple[dict, str | None]:  # R15-6: 境界フォームを検証する
    cleaned: dict = {}  # R15-6: 正常化した値を入れる
    for f in BOUNDARY_FIELDS:  # R15-6: 定義に従って各項目を処理する
        raw = form.get(f.key, str(f.default))  # R15-6: 無ければ既定値
        try:
            v = int(raw)  # R15-6: int化する
        except ValueError:
            return {}, f"{f.key} は整数で入力してください"  # R15-6: 型エラー
        if v < f.min or v > f.max:
            return {}, f"{f.key} は {f.min}〜{f.max} の範囲で入力してください"  # R15-6: rangeエラー
        cleaned[f.key] = v  # R15-6: 正常値を格納する
    return cleaned, None  # R15-6: 正常