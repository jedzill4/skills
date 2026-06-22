"""Selection + plan-building + apply. Clean-adds only; merges are deferred."""

from __future__ import annotations

import subprocess
from pathlib import Path

from scaffolding import console
from scaffolding.components import REGISTRY, Component, Context, lookup
from scaffolding.facts import Facts
from scaffolding.plan import Decisions, Disposition, Op, Plan
from scaffolding.settings import Settings


class NotAGitRepo(Exception):
    pass


class UnknownComponent(Exception):
    pass


def _initial_selection(
    requested: list[str], facts: Facts, settings: Settings
) -> tuple[list[str], bool]:
    """Return (component names, explicit) before skip/dep resolution."""
    if requested:
        for name in requested:
            if lookup(name) is None:
                raise UnknownComponent(name)
        return list(dict.fromkeys(requested)), True
    names = [c.name for c in REGISTRY if c.default_on and c.gate(facts)]
    if settings.with_ci and "ci" not in names:
        names.append("ci")
    return names, False


def _gate_notices(names: list[str], facts: Facts) -> list[str]:
    """Warn when an explicitly-selected component's gate is not satisfied."""
    out = []
    for n in names:
        c = lookup(n)
        if c and not c.gate(facts):
            out.append(f"{n}: gate not satisfied for this repo — including anyway (explicit)")
    return out


def _resolve_deps(names: list[str], skip: list[str], facts: Facts) -> list[str]:
    """Append missing dependencies in place; return the notices for them."""
    notices = []
    for n in list(names):
        c = lookup(n)
        if not c:
            continue
        for dep in c.deps(facts):
            if dep not in names and dep not in skip:
                names.append(dep)
                notices.append(f"{dep} (required by {n})")
    return notices


def select_components(
    requested: list[str],
    skip: list[str],
    facts: Facts,
    settings: Settings,
) -> tuple[list[Component], list[str]]:
    """Resolve the component set. Returns (ordered components, notices)."""
    skip = skip or []
    names, explicit = _initial_selection(requested, facts, settings)
    if settings.skip_ci and "ci" in names:
        names.remove("ci")
    names = [n for n in names if n not in skip]

    notices: list[str] = []
    if explicit:
        notices += _gate_notices(names, facts)
    if not settings.no_deps:
        notices += _resolve_deps(names, skip, facts)

    ordered = [c for c in REGISTRY if c.name in names]
    return ordered, notices


def build_plan(
    root: Path,
    facts: Facts,
    settings: Settings,
    *,
    requested: list[str] | None = None,
    skip: list[str] | None = None,
    decisions: Decisions | None = None,
    interactive: bool = False,
) -> Plan:
    components, notices = select_components(requested or [], skip or [], facts, settings)
    ctx = Context(
        root=root,
        facts=facts,
        settings=settings,
        decisions=decisions if decisions is not None else Decisions(),
        interactive=interactive,
    )
    plan = Plan(facts=facts, notices=notices)
    for comp in components:
        plan.ops.extend(comp.plan(ctx))
    plan.decisions = list(ctx._decisions)
    return plan


def _apply_write(op: Op) -> None:
    if op.path is None:
        raise ValueError(f"write op for {op.target} has no path")
    p = Path(op.path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(op.content or "", encoding="utf-8")


def _apply_append(op: Op) -> None:
    if op.path is None:
        raise ValueError(f"append op for {op.target} has no path")
    p = Path(op.path)
    p.parent.mkdir(parents=True, exist_ok=True)
    cur = p.read_text(encoding="utf-8") if p.exists() else ""
    if cur and not cur.endswith("\n"):
        cur += "\n"
    p.write_text(cur + (op.content or ""), encoding="utf-8")


def _apply_add(op: Op) -> None:
    if op.kind == "write":
        _apply_write(op)
    elif op.kind == "append":
        _apply_append(op)


def _apply_run(op: Op) -> bool:
    """Run op.cmd. Return True on success or non-fatal failure, False otherwise."""
    console.run(op.target)
    if op.cmd is None:
        console.warn(f"{op.target}: no command")
        return op.optional
    try:
        ok = subprocess.run(op.cmd).returncode == 0
    except OSError as exc:
        ok = False
        console.warn(f"{op.target}: {exc}")
    if ok:
        return True
    if op.optional:
        console.skip(f"{op.target} failed (non-fatal)")
        return True
    console.warn(f"{op.target} failed")
    return False


def apply(plan: Plan, root: Path) -> int:
    """Execute ADD/RUN ops; report SKIP/DEFER/WARN. Returns process-style code."""
    console.print_notices(plan)
    errors = 0
    for op in plan.ops:
        label = op.target + (f" — {op.detail}" if op.detail else "")
        d = op.disposition
        if d is Disposition.ADD:
            _apply_add(op)
            console.add(label)
        elif d is Disposition.RUN:
            errors += 0 if _apply_run(op) else 1
        elif d is Disposition.DEFER:
            console.defer(label)
        elif d is Disposition.SKIP:
            console.skip(label)
        elif d is Disposition.WARN:
            console.warn(label)
    return 1 if errors else 0
