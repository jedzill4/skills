# scaffolding

Personal repo bootstrap + agent skills for OpenCode-first development.

This repo does two things:

1. **Bootstrap a repo** with my workspace defaults (gitignore, local OpenCode
   config, `AGENTS.md` guidance, optional prek hooks, ast-grep, CI, Varlock
   secrets) via a small Python CLI. This is a one-time-per-repo operation, run as
   an *agentic install* or directly — not an installed skill.
2. **Ship a couple of recurring skills** (`journalist`, `handoff`) that you
   install once and use repeatedly.

Most engineering workflow skills I use come from Matt Pocock's
[`skills`](https://github.com/mattpocock/skills). This repo intentionally does
not vendor those; it only contains my own additions.

## Bootstrap a repo

Run this from the root of the repo you want to set up.

**Existing working repo (recommended): let an agent do it.** The bootstrap needs
judgment — new-vs-existing detection, additive JSONC/`AGENTS.md` merges, Python
detection, and per-item conflict resolution. The CLI does the deterministic
clean-adds; the agent drives it and handles merges. Point your agent at the guide:

> Set up this repo by following the instructions here:
> `https://raw.githubusercontent.com/jedzill4/scaffolding/main/guide.md`
> Don't summarize it — follow every step.

**New / empty repo (fast path): run the CLI directly.** It does clean adds only
and refuses to touch existing files, deferring any merge to the agent.

Straight from git via `uvx` (no PyPI):

```bash
uvx --from git+https://github.com/jedzill4/scaffolding scaffolding install
```

Or via the bootstrap shim (also installs `uv` if missing — preserves the classic
one-liner):

```bash
curl -fsSL https://raw.githubusercontent.com/jedzill4/scaffolding/main/install.sh | bash
```

The installer is idempotent — safe to re-run. Existing files are never edited or
overwritten; they are reported as `[defer]` for the agent to merge.

### Commands

```
scaffolding install [components…]   # clean-adds (all default-on, or just the named ones)
scaffolding install --yes           # non-interactive / CI (conservative defaults)
scaffolding install --dry-run       # render the plan, write nothing
scaffolding plan --json             # machine-readable plan for the agent path
scaffolding list                    # available components (gate / default / what they add)
scaffolding check                   # verify bootstrap completeness (nonzero exit on failure)
scaffolding doctor                  # diagnose environment + tools
```

Components: `gitignore opencode prek ast-grep pyproject ci agents skills
varlock` (all default-on except `ci`, which is opt-in). Scope with positional
names or `--skip a,b`. Useful flags: `--agent`, `--ci/--no-ci`, `--ci-parts`,
`--name`, `--description`, `--varlock/--no-varlock`, `--no-deps`. Legacy env vars
(`AGENT`, `SKIP_SKILLS`, `SKIP_VARLOCK`, `WITH_CI`/`SKIP_CI`, `ASSUME_YES`) are
honored.

There is no `uninstall`: the installer requires a git repo, so `git status` /
`git checkout` / `git clean` are the undo mechanism.

## Installed skills

These are real skills you install once per agent and use repeatedly. Default
agent target is OpenCode.

Install selected upstream skills from Matt Pocock:

```bash
npx skills add mattpocock/skills --agent opencode --yes --skill setup-matt-pocock-skills diagnose grill-with-docs triage improve-codebase-architecture tdd to-issues to-prd zoom-out prototype grill-me write-a-skill
```

Then install my local skills from this repo:

```bash
npx skills add jedzill4/scaffolding --agent opencode --yes --skill journalist handoff
```

If installing from a checkout, run from this repo:

```bash
npx skills add . --agent opencode --yes --skill journalist handoff --full-depth
```

Use `--agent claude-code` or `--agent codex` instead only when that is the agent
you actually use.

## Upstream skills from Matt Pocock

- `diagnose`, `tdd` — engineering quality workflows.
- `to-prd`, `to-issues`, `triage` — planning and issue workflows.
- `prototype` — throwaway code/UI prototyping.
- `improve-codebase-architecture`, `zoom-out` — architecture and system understanding workflows.
- `grill-me`, `grill-with-docs`, `write-a-skill` — meta/collaboration workflows.

## What's in this repo

- `scaffolding/` — the bootstrap CLI (Cyclopts + Questionary + pydantic-settings
  + Rich). `cli.py`, `engine.py`/`plan.py`, `components.py`, and `templates/`
  (OpenCode config, prek hooks, pyproject, ast-grep rules, CI workflows,
  AGENTS.md section).
- `install.sh` — thin bootstrap shim (ensure `uv`, then run the CLI from git).
- `guide.md` — the agentic-install guide (judgment layer).
- `skills/productivity/journalist` — local daily session journals under `.journals/`.
- `skills/productivity/handoff` — compact the current session into a temp-dir handoff for another agent.
