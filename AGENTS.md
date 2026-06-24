# Agent Notes

## Repo Layout

- `scaffolding/` — the bootstrap CLI (Python package, run via
  `uvx --from git+…/scaffolding scaffolding …`). `cli.py` (Cyclopts commands),
  `engine.py`/`plan.py` (build + apply, clean-adds only), `components.py`
  (component registry), `templates/` (bundled package data). The CLI is the
  single deterministic engine; keep it **clean-adds-only** — it must never edit,
  merge, or overwrite existing target files (existing targets are deferred).
- `install.sh` — thin bootstrap shim (ensure `uv`, then `uvx … scaffolding
  install`). Keep it minimal and keep its raw URL pointing at
  `jedzill4/scaffolding` on `main`.
- `guide.md` — the agentic-install guide (judgment layer that drives the CLI and
  handles merges). Keep template raw URLs pointing at `jedzill4/scaffolding`.
- `skills/` — actual installed skills (`journalist`, `handoff`).

After changing the CLI, validate with `uv run ruff check scaffolding` and
`uv run scaffolding --help`.

## Skill Development

After creating or editing any skill under `skills/`, validate its `SKILL.md`
before committing:

```bash
tessl skill review <SKILL.md>
```

Run it against each changed skill (e.g. `tessl skill review skills/productivity/journalist/SKILL.md`)
and resolve the reported issues before publishing.


## Domain docs

Single-context — `CONTEXT.md` + `docs/adr/` at the repo root (created lazily).
See `docs/agents/domain.md`.

## Repo Workspace Defaults

- Use `.scratch/` for temporary plans, prd issue drafts, and disposable notes.
- Use `.tmp/` for generated local artifacts that should not be committed.
- Use `.worktrees/` for local Git worktrees when needed.
- Use `.journals/` for local/private session journals when using the `journalist` skill.
- Preserve unrelated user changes and avoid destructive Git commands unless explicitly requested.
