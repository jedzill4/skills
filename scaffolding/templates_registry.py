"""Access to bundled template files (package data under scaffolding/templates)."""

from __future__ import annotations

from importlib.resources import files


def template_path(rel: str):
    p = files("scaffolding").joinpath("templates")
    for part in rel.split("/"):
        p = p.joinpath(part)
    return p


def template_text(rel: str) -> str:
    return template_path(rel).read_text(encoding="utf-8")
