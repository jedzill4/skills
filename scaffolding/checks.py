"""`check` — completeness verification from the guide Verify checklist."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from scaffolding.components import AGENTS_MARKER, GITIGNORE_ENTRIES


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def _strip_jsonc(text: str) -> str:
    # remove // line comments and /* */ block comments, then trailing commas
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"(^|\s)//[^\n]*", r"\1", text)
    return re.sub(r",(\s*[}\]])", r"\1", text)


def _git_tracked(root: Path, rel: str) -> bool:
    try:
        out = subprocess.run(
            ["git", "ls-files", "--error-unmatch", rel],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return out.returncode == 0
    except Exception:
        return False


def _gitignored(root: Path, rel: str) -> bool:
    try:
        out = subprocess.run(
            ["git", "check-ignore", "-q", rel],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return out.returncode == 0
    except Exception:
        return False


def run_checks(root: Path | None = None) -> list[CheckResult]:
    root = root or Path.cwd()
    results: list[CheckResult] = []

    gi = root / ".gitignore"
    if gi.exists():
        present = {ln.rstrip() for ln in gi.read_text(encoding="utf-8").splitlines()}
        missing = [e for e in GITIGNORE_ENTRIES if e not in present]
        results.append(
            CheckResult(
                ".gitignore entries",
                not missing,
                "all present" if not missing else f"missing: {', '.join(missing)}",
            )
        )
    else:
        results.append(CheckResult(".gitignore entries", False, ".gitignore missing"))

    prek = root / "prek.toml"
    if prek.exists():
        body = prek.read_text(encoding="utf-8")
        results.append(
            CheckResult(
                "prek betterleaks hook",
                "betterleaks" in body,
                "present" if "betterleaks" in body else "betterleaks hook missing",
            )
        )
    else:
        results.append(CheckResult("prek.toml", False, "prek.toml missing"))

    oc = root / "opencode.jsonc"
    if oc.exists():
        try:
            data = json.loads(_strip_jsonc(oc.read_text(encoding="utf-8")))
            need = [k for k in ("$schema", "plugin", "permission") if k not in data]
            results.append(
                CheckResult(
                    "opencode.jsonc valid",
                    not need,
                    "ok" if not need else f"missing keys: {', '.join(need)}",
                )
            )
        except (ValueError, OSError) as exc:
            results.append(CheckResult("opencode.jsonc valid", False, f"parse error: {exc}"))
    else:
        results.append(CheckResult("opencode.jsonc", False, "missing"))

    schema = root / ".env.schema"
    if schema.exists():
        tracked = _git_tracked(root, ".env.schema")
        results.append(
            CheckResult(
                ".env.schema tracked",
                tracked,
                "tracked" if tracked else "exists but not tracked by git",
            )
        )
    else:
        results.append(CheckResult(".env.schema", False, "missing (run varlock)"))

    env_ignored = _gitignored(root, ".env")
    results.append(
        CheckResult(
            ".env ignored", env_ignored, "ignored" if env_ignored else ".env is not gitignored"
        )
    )

    sg = root / "sgconfig.yml"
    prek_has_astgrep = prek.exists() and "ast-grep" in prek.read_text(encoding="utf-8")
    if prek_has_astgrep:
        rules = (
            list((root / "ast-grep" / "rules").glob("*.yml"))
            if (root / "ast-grep" / "rules").exists()
            else []
        )
        ok = sg.exists() and bool(rules)
        results.append(
            CheckResult(
                "ast-grep config",
                ok,
                "ok" if ok else "ast-grep hook present but sgconfig.yml/rules missing",
            )
        )

    am = root / "AGENTS.md"
    if am.exists():
        has = AGENTS_MARKER in am.read_text(encoding="utf-8")
        results.append(
            CheckResult("AGENTS.md section", has, "present" if has else f"{AGENTS_MARKER} missing")
        )
    else:
        results.append(CheckResult("AGENTS.md", False, "missing"))

    return results
