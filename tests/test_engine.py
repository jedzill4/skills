"""Engine/plan tests: clean-adds-only behavior, gating, deps, idempotency."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scaffolding.engine import UnknownComponent, apply, build_plan, select_components
from scaffolding.facts import detect
from scaffolding.plan import Decisions, Disposition
from scaffolding.settings import Settings


def _git_init(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git_init(tmp_path)
    return tmp_path


def _facts(root: Path):
    return detect(root, probe_visibility=False)


def _targets(plan, disp: Disposition) -> list[str]:
    return [op.target for op in plan.by(disp)]


def test_nonpython_full_install_excludes_python_and_ci(repo: Path):
    plan = build_plan(repo, _facts(repo), Settings(skip_skills=True, skip_varlock=True))
    comps = {op.component for op in plan.ops}
    assert "ast-grep" not in comps
    assert "pyproject" not in comps
    assert "ci" not in comps
    assert ".gitignore" in _targets(plan, Disposition.ADD)
    assert "opencode.jsonc" in _targets(plan, Disposition.ADD)


def test_python_repo_includes_astgrep_and_pyproject(repo: Path):
    (repo / "app.py").write_text("x = 1\n")
    plan = build_plan(repo, _facts(repo), Settings(skip_skills=True, skip_varlock=True))
    targets = _targets(plan, Disposition.ADD)
    assert "sgconfig.yml" in targets
    assert "pyproject.toml" in targets
    keys = {d.key for d in plan.decisions}
    assert {"pyproject_name", "pyproject_description"} <= keys


def test_prek_pulls_astgrep_dependency_on_python(repo: Path):
    (repo / "pyproject.toml").write_text("[project]\nname='x'\n")
    plan = build_plan(repo, _facts(repo), Settings(), requested=["prek"])
    comps = {op.component for op in plan.ops}
    assert "ast-grep" in comps
    assert any("required by prek" in n for n in plan.notices)


def test_no_deps_suppresses_dependency(repo: Path):
    (repo / "app.py").write_text("x = 1\n")
    plan = build_plan(repo, _facts(repo), Settings(no_deps=True), requested=["prek"])
    comps = {op.component for op in plan.ops}
    assert "ast-grep" not in comps


def test_explicit_selection_overrides_gate_with_notice(repo: Path):
    plan = build_plan(repo, _facts(repo), Settings(), requested=["pyproject"])
    assert any("gate not satisfied" in n for n in plan.notices)
    assert "pyproject.toml" in _targets(plan, Disposition.ADD)


def test_unknown_component_raises(repo: Path):
    with pytest.raises(UnknownComponent):
        build_plan(repo, _facts(repo), Settings(), requested=["nope"])


def test_apply_is_clean_adds_only_and_idempotent(repo: Path):
    settings = Settings(skip_skills=True, skip_varlock=True)
    plan = build_plan(repo, _facts(repo), settings)
    apply(plan, repo)
    assert (repo / ".gitignore").exists()
    assert (repo / "opencode.jsonc").exists()

    original = (repo / "opencode.jsonc").read_text()
    # Re-run: existing files must be deferred, not overwritten.
    plan2 = build_plan(repo, _facts(repo), settings)
    assert "opencode.jsonc" in _targets(plan2, Disposition.DEFER)
    apply(plan2, repo)
    assert (repo / "opencode.jsonc").read_text() == original


def test_pyproject_substitution(repo: Path):
    (repo / "app.py").write_text("x = 1\n")
    decisions = Decisions(pyproject_name="demo-pkg", pyproject_description="A demo")
    plan = build_plan(repo, _facts(repo), Settings(), requested=["pyproject"], decisions=decisions)
    apply(plan, repo)
    body = (repo / "pyproject.toml").read_text()
    assert 'name = "demo-pkg"' in body
    assert 'description = "A demo"' in body
    assert "replace-me" not in body


def test_gitignore_partial_append(repo: Path):
    (repo / ".gitignore").write_text(".env\n")
    plan = build_plan(repo, _facts(repo), Settings(), requested=["gitignore"])
    apply(plan, repo)
    lines = (repo / ".gitignore").read_text().splitlines()
    assert ".env" in lines
    assert ".journals/" in lines
    assert lines.count(".env") == 1


def test_select_skip(repo: Path):
    comps, _ = select_components([], ["opencode"], _facts(repo), Settings(skip_skills=True))
    names = {c.name for c in comps}
    assert "opencode" not in names
    assert "gitignore" in names
