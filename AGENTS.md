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

## Agent skills

### Issue tracker

Local markdown — issues and PRDs live under `.scratch/<feature>/`. External PRs
are not a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical role strings (`needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`), recorded as a `Status:` line per issue file. See
`docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` + `docs/adr/` at the repo root (created lazily).
See `docs/agents/domain.md`.

## Repo Workspace Defaults

- Use `.scratch/` for temporary plans, issue drafts, and disposable notes.
- Use `.tmp/` for generated local artifacts that should not be committed.
- Use `.worktrees/` for local Git worktrees when needed.
- Use `.journals/` for local/private session journals when using the `journalist` skill.
- Preserve unrelated user changes and avoid destructive Git commands unless explicitly requested.

### Resource Limits For Heavy Commands

Run computationally expensive commands (heavy builds, full test suites, data jobs, memory-hungry tooling) under `systemd-run` so a runaway process cannot exhaust the machine:

- Cap memory with `MemoryMax` (hard limit; process is killed if exceeded) and disable swap thrashing with `MemorySwapMax=0`.
- Cap CPU with `CPUQuota` (e.g. `400%` = up to 4 cores).
- Use a transient user scope (no root needed). If `systemd-run` is unavailable, fall back to `ulimit -v` for a memory cap.

Measure and log wall time and peak memory with `/usr/bin/time -v`, appending to `.tmp/logs/<command>/<date>_wall-stats.log`. Read the latest log before re-running to estimate limits instead of guessing:

```bash
cmd=build; ts=$(date +%Y-%m-%dT%H-%M-%S)
log=.tmp/logs/$cmd/${ts}_wall-stats.log; mkdir -p ".tmp/logs/$cmd"
systemd-run --user --scope -p MemoryMax=4G -p MemorySwapMax=0 -p CPUQuota=400% \
  /usr/bin/time -v -o "$log" <command>
```

Run long commands in the background with a saved PID so they are not tied to the agent tool timeout, and delegate polling to a cheap monitor sub-agent (e.g. Haiku) that runs a `while kill -0 <pid>; do sleep <n>; done` loop and reports only the final exit status, output tail, and stats log path. This keeps the main session from being poisoned by repeated status checks.

```bash
( systemd-run --user --scope -p MemoryMax=4G -p CPUQuota=400% \
    /usr/bin/time -v -o "$log" <command> ) >".tmp/logs/$cmd/${ts}.out" 2>&1 &
echo $! > ".tmp/logs/$cmd/${ts}.pid"
```

Scripts we write ourselves must emit periodic progress to the output log (current step, counts, percent, or heartbeat with a timestamp) so the monitor can tell what they are doing. Flush each line (e.g. Python `print(..., flush=True)` or `PYTHONUNBUFFERED=1`) so progress appears live. The monitor always `tail`s the latest lines of the `.out` log — never reads the full log — to avoid poisoning the session with bulk output.

A consistently too-expensive step is a signal of poor code that needs optimization, not a reason to keep raising the limits — flag it.
