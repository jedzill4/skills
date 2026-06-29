"""Low-level clean-adds-only Op builders shared across components.

This is the base layer: it depends only on the plan model, so both ``components``
and ``agent_config`` can import it without creating an import cycle.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffolding.plan import Disposition, Op

if TYPE_CHECKING:
    from pathlib import Path


def write_if_absent(component: str, dest: Path, content: str, label: str, guide_url: str) -> Op:
    """Write ``content`` to ``dest`` when absent; defer (never overwrite) when present."""
    if dest.exists():
        return Op(
            component,
            "noop",
            label,
            Disposition.DEFER,
            detail=f"already exists — left untouched. Merge via guide: {guide_url}",
        )
    return Op(component, "write", label, Disposition.ADD, path=str(dest), content=content)


def symlink_if_absent(component: str, link: Path, target: str, label: str, guide_url: str) -> Op:
    """Symlink ``link`` -> ``target`` when absent; defer (never replace) when present."""
    if link.exists() or link.is_symlink():
        return Op(
            component,
            "noop",
            label,
            Disposition.DEFER,
            detail=f"already exists — left untouched. Bridge manually via guide: {guide_url}",
        )
    return Op(
        component,
        "symlink",
        label,
        Disposition.ADD,
        path=str(link),
        content=target,
        detail=f"symlink -> {target}",
    )
