"""Rich output helpers: status lines, plan table, panels."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .plan import Disposition, Plan

console = Console()
err_console = Console(stderr=True)

_STYLE = {
    Disposition.ADD: ("green", "add"),
    Disposition.SKIP: ("yellow", "skip"),
    Disposition.DEFER: ("yellow", "defer"),
    Disposition.RUN: ("cyan", "run"),
    Disposition.WARN: ("red", "warn"),
}


def add(msg: str) -> None:
    console.print(f"[green]\\[add][/green]   {msg}")


def skip(msg: str) -> None:
    console.print(f"[yellow]\\[skip][/yellow]  {msg}")


def defer(msg: str) -> None:
    console.print(f"[yellow]\\[defer][/yellow] {msg}")


def info(msg: str) -> None:
    console.print(f"[blue]\\[info][/blue]  {msg}")


def warn(msg: str) -> None:
    console.print(f"[red]\\[warn][/red]  {msg}")


def run(msg: str) -> None:
    console.print(f"[cyan]\\[run][/cyan]   {msg}")


def print_notices(plan: Plan) -> None:
    for note in plan.notices:
        info(note)


def render_plan_table(plan: Plan, title: str = "Plan") -> None:
    table = Table(title=title, show_lines=False, expand=False)
    table.add_column("disp", no_wrap=True)
    table.add_column("component", no_wrap=True)
    table.add_column("target")
    table.add_column("detail", overflow="fold")
    for op in plan.ops:
        color, label = _STYLE.get(op.disposition, ("white", op.disposition.value))
        table.add_row(f"[{color}]{label}[/{color}]", op.component, op.target, op.detail)
    console.print(table)
    if plan.decisions:
        dt = Table(title="Decisions needed (you decide)", show_lines=False)
        dt.add_column("tier", no_wrap=True)
        dt.add_column("key", no_wrap=True)
        dt.add_column("question")
        dt.add_column("default")
        for d in plan.decisions:
            dt.add_row(str(d.tier), d.key, d.question, d.default)
        console.print(dt)
