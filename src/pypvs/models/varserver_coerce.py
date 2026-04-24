"""Coerce varserver / JSON dict values (missing keys and explicit nulls)."""

from __future__ import annotations

from typing import Any


def float_var(data: dict[str, Any], key: str, default: float = 0.0) -> float:
    v = data.get(key)
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def int_var(data: dict[str, Any], key: str, default: int = 0) -> int:
    v = data.get(key)
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def str_var(data: dict[str, Any], key: str, default: str | None = "") -> str | None:
    v = data.get(key)
    return default if v is None else str(v)
