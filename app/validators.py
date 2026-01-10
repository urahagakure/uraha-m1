from __future__ import annotations

from typing import Mapping, Tuple


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
