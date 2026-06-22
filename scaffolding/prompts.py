"""Questionary wrappers that fall back to defaults under --yes / non-TTY.

Mirrors the ``ask_yes_no`` semantics of the original install.sh: interactive
only when both stdin and stdout are a TTY and ``assume_yes`` is not set;
otherwise return the default without prompting (deterministic CI/agent runs).
"""

from __future__ import annotations

import sys


def is_interactive(assume_yes: bool) -> bool:
    return (not assume_yes) and sys.stdin.isatty() and sys.stdout.isatty()


def confirm(question: str, default: bool, *, assume_yes: bool) -> bool:
    if not is_interactive(assume_yes):
        return default
    import questionary

    res = questionary.confirm(question, default=default).ask()
    return default if res is None else bool(res)


def text(question: str, default: str, *, assume_yes: bool) -> str:
    if not is_interactive(assume_yes):
        return default
    import questionary

    res = questionary.text(question, default=default).ask()
    return res.strip() if res and res.strip() else default


def select(question: str, choices: list[str], default: str, *, assume_yes: bool) -> str:
    if not is_interactive(assume_yes):
        return default
    import questionary

    res = questionary.select(question, choices=choices, default=default).ask()
    return res or default


def checkbox(
    question: str, choices: list[str], default: list[str], *, assume_yes: bool
) -> list[str]:
    if not is_interactive(assume_yes):
        return default
    import questionary

    opts = [questionary.Choice(c, checked=(c in default)) for c in choices]
    res = questionary.checkbox(question, choices=opts).ask()
    return res if res else default
