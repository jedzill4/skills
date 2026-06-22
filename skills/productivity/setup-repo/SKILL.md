---
name: setup-repo
description: "Initialize a repo with personal workspace defaults: gitignore entries, local OpenCode config, AGENTS.md guidance, and optional prek pre-commit hooks. Use when starting a new project, onboarding to a repo, bootstrapping workspace setup, or normalizing a project for day-to-day agent-assisted development."
---

# Setup Repo

Prepare an existing project repo with the small defaults I usually want before active work starts. Keep this minimal: do not scaffold application code, install dependencies, or add language-specific tooling unless the user asks.

## Workflow

1. Inspect the repo root for existing `.gitignore`, `.opencode/`, `opencode.json`, `opencode.jsonc`, `prek.toml`, `AGENTS.md`, `CLAUDE.md`, `.env.schema`, and any `.env*` files.
2. Decide whether this is a clean setup (new/empty repo) or a migration into an existing working repo. See [New vs. Existing Repos (Migration)](#new-vs-existing-repos-migration). For a migration, present the installation plan and get the user's decision before writing anything beyond inspection.
3. Preserve existing content. Only add missing files, missing lines, or missing config keys. Never delete, replace, reorder, or simplify existing data without explicit user authorization.
4. Prefer repo-local OpenCode config at `.opencode/opencode.jsonc` so the settings travel with this repo and do not overwrite global config.
5. Add or update the managed workspace section in `AGENTS.md`. Create `AGENTS.md` if it does not exist. Do not edit `CLAUDE.md` for this skill unless the user explicitly asks.
6. Validate that any JSON/JSONC you wrote parses or is accepted by the relevant tool.

## New vs. Existing Repos (Migration)

How aggressive this skill can be depends on the repo's starting state.

**New or empty repo (clean setup).** If the repo has no conflicting config — no `.gitignore` entries, no `.opencode/` config, no `prek.toml`, no `AGENTS.md` section, no `.env*` or `.env.schema` — just apply every default directly. There is nothing to preserve, so write the files, install the skills, and run `varlock init` without further negotiation.

**Existing working repo (migration).** When any of these already exist, treat the setup as a migration: do not silently change a project people are actively using. Instead, inspect the current state, then **propose an installation plan and let the user decide** before applying it. The plan should sort every intended change into three buckets:

- **Clean adds (safe, will apply automatically):** files or entries that are missing entirely and only add new content — e.g. a missing `.gitignore` line, a brand-new `.opencode/opencode.jsonc`, a fresh `AGENTS.md` section. List them but proceed once approved.
- **Merges (additive but touch existing files):** adding missing keys to an existing `opencode.jsonc`, appending hooks to an existing `prek.toml`, adding the workspace section to an existing `AGENTS.md`, or adding tool sections to an existing `pyproject.toml`. Show what will be inserted and confirm there are no collisions.
- **Conflicts / needs decision (will NOT change without explicit approval):** anything that would remove, replace, reorder, or restructure existing content, or where the user's value differs from the default — e.g. an existing `.env.example`/`.env.schema` that `varlock init` might rewrite, a `.gitignore` that already handles `.env` differently, permission rules that conflict with the user's, or existing pre-commit hooks. Explain the conflict and let the user choose per item; never auto-resolve.

Present this as a short checklist (clean adds / merges / conflicts), state what you will and will not touch, and wait for the user's go-ahead. Default to the most conservative option for anything in the conflicts bucket, and skip rather than overwrite when unsure.

## Non-Destructive Edits

This skill is additive by default:

- If a file exists, update it in place by adding only the missing entries.
- If a key already exists in `opencode.jsonc`, preserve its current value and merge only missing nested keys or array items.
- If the desired change would require removing, renaming, replacing, or restructuring existing content, stop and ask the user first.
- Do not normalize formatting across the whole file just because it differs from the examples below.

## `.gitignore`

Ensure these workspace-only directories are ignored at the repo root:

```
.env
.tmp/
.scratch/
.worktrees/
.journals/
```

## `prek.toml`

Create or update `prek.toml` only additively. Always include the generic hooks below when missing. Include Python-specific hooks only when the repo has a root `pyproject.toml`, another clear Python layout, or the user asks for Python checks.

Use the bundled templates:

- [prek-generic.toml](./prek-generic.toml) — generic safety and formatting hooks.
- [prek-python.toml](./prek-python.toml) — Python hooks using `uv`, `ruff`, `pyrefly`, and `ast-grep`.
- [pyproject-template.toml](./pyproject-template.toml) — starter root Python config with `hatchling`, `ruff`, `pyrefly`, and `pytest` sections.

Assume Python lives at the repo root by default, with `pyproject.toml` at the root. Change paths to a subdirectory such as `backend/` only if the repo layout or user explicitly demands it. Do not add Python-specific hooks to non-Python repos unless the user asks.

If a Python repo has no `pyproject.toml`, create one from `pyproject-template.toml` and replace placeholder project metadata. If `pyproject.toml` already exists, only add missing tool sections and never replace dependencies or project metadata without explicit approval.

## `.opencode/opencode.jsonc`

Create or update this repo-local OpenCode config. Use JSONC because comments and trailing commas are intentional.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [
    "opencode-sessions-explorer",
    "opencode-varlock@latest",
  ],
  "permission": {
    "external_directory": {
      "~/.local/share/opencode/**": "allow"
    },
    "skill": {
      "*": "allow"
    },
    "read": {
           "*.env*": "deny",
           "*.env.schema": "allow",
           "*.env.example": "allow",
           "*.pem": "deny",
           "*.key": "deny",
           "*credentials*": "deny",
           "*.pgpass": "deny",
           "*varlock.config*": "deny",
         },
         "write": {
           "*.env*": "deny",
           "*.pem": "deny",
           "*.key": "deny",
           "*varlock.config*": "deny",
         },
         "edit": {
           "*.env*": "deny",
           "*.pem": "deny",
           "*.key": "deny",
           "*varlock.config*": "deny",
         },
         "bash": {
           "cat *.env*": "deny",
           "less *.env*": "deny",
           "more *.env*": "deny",
           "head *.env*": "deny",
           "tail *.env*": "deny",
           "grep * .env*": "deny",
           "sed * .env*": "deny",
           "awk * .env*": "deny",
           "cut * .env*": "deny",
           "sort .env*": "deny",
           "dd if=.env*": "deny",
           "tee * .env*": "deny",
           "xxd .env*": "deny",
           "echo $*": "deny",
           "python*getenv*": "deny",
           "python*os.environ*": "deny",
           "python*open*env*": "deny",
           "node*process.env*": "deny",
           "node*readFileSync*env*": "deny",
           "ruby*File.read*env*": "deny",
           "printenv*": "deny",
           "env": "deny",
           "env *": "deny",
           "export -p": "deny",
           "declare -x": "deny",
           "compgen -v": "deny",
           "compgen -A variable": "deny",
           "typeset -x": "deny",
           "source .env*": "deny",
           ". .env*": "deny",
           "set -a*": "deny",
           "curl *env*": "deny",
           "wget *env*": "deny",
           "varlock printenv*": "deny",
           "varlock load --show*": "deny",
           "varlock load --format*": "deny",
           "varlock load -f*": "deny",
           "*base64*|*bash*": "deny",
           "*base64*|*sh*": "deny",
           "npm test": "allow",
           "npm run *": "allow",
           "bun test": "allow",
           "bun run *": "allow",
           "git *": "allow",
           "ls *": "allow",
         }
  },
  
  "mcp": {}
}
```

If `opencode-sessions-explorer` is not installed and the user wants it, install/configure it using the project's normal OpenCode plugin workflow. Otherwise keep the config but mention the plugin must be available for the entry to load.

## Varlock Secret Management

Use [Varlock](https://varlock.dev) for environment and secret management so secrets stay out of the repo and out of agent context. The `opencode-varlock@latest` plugin in `.opencode/opencode.jsonc` and the `.env*` permission guards above assume Varlock is installed and the repo carries a committed `.env.schema`.

Install Varlock and scaffold the schema additively. Never overwrite an existing `.env.schema` or `.env` without explicit user approval.

1. **Install as a dependency.** For Node.js/TypeScript projects (Node 22+), add `varlock` and scaffold the schema in non-interactive agent mode so it does not prompt:

   ```bash
   npx varlock init --agent
   ```

   Use the matching package-manager variant when the repo declares one: `pnpm dlx varlock init --agent`, `bunx varlock init --agent`, `vlx varlock init --agent`, or `yarn dlx varlock init --agent`.

   For non-JS repos, or when a global CLI is preferred, install the standalone binary instead and then run the wizard:

   ```bash
   brew install dmno-dev/tap/varlock   # or: curl -sSfL https://varlock.dev/install.sh | sh -s
   varlock init
   ```

   `varlock init` installs `varlock`, scans for existing `.env` files, and creates a root `.env.schema`. It may also offer to remove an existing `.env.example` and add `@type` decorators — review those changes; do not let it delete files the user wants to keep.

2. **Install the Varlock agent skill** so future sessions know how to author `.env.schema` files:

   ```bash
   npx skills add dmno-dev/varlock --agent opencode --yes
   ```

3. **Commit `.env.schema`, never `.env`.** Confirm `.env` is ignored (see [`.gitignore`](#gitignore) above) and that `.env.schema` is tracked. The schema is the source of truth for required variables; real values live only in local `.env` files or the user's secret backend.

## Skill Installation

When setting up agent skills for a repo, install the selected upstream Matt Pocock skills from `mattpocock/skills`, then install this repo's two local skills. Do not vendor or install every upstream skill. Default to OpenCode:

```bash
npx skills add mattpocock/skills --agent opencode --yes --skill diagnose grill-with-docs triage improve-codebase-architecture tdd to-issues to-prd zoom-out prototype grill-me write-a-skill
npx skills add jedzill4/skills --agent opencode --yes --skill setup-repo journalist handoff
npx skills add dmno-dev/varlock --agent opencode --yes
```

If running from a local checkout of this skills repo, keep the Matt Pocock command as-is and install local skills with `npx skills add . --agent opencode --yes --skill setup-repo journalist handoff --full-depth`.

If the repo clearly uses Claude Code or Codex instead of OpenCode, ask before switching `--agent` to `claude-code` or `codex`.

## `AGENTS.md`

The core task of this skill is to write the managed section below into `AGENTS.md` so the rules apply to every future agent session in this repo. If the file already exists, add the section if missing. If the section exists, update only the lines inside this section and preserve everything else. If creating a new `AGENTS.md`, add `# Agent Notes` before this section.

Write this block verbatim:

```markdown
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
```

For richer agent-skill docs, use Matt Pocock's upstream `setup-matt-pocock-skills` skill if installed.

## Verify

- `.gitignore` contains `.env`, `.tmp/`, `.scratch/`, `.worktrees/`, and `.journals/` exactly once.
- `prek.toml` contains the generic hooks, and Python-specific hooks are present only when appropriate for the repo.
- Python repos have a valid `pyproject.toml`; existing project metadata and dependencies were preserved.
- `.opencode/opencode.jsonc` is valid JSONC and includes the schema, plugin, permission, and `mcp` sections.
- Varlock is installed (as a `package.json` dependency or standalone binary) and a root `.env.schema` exists and is tracked by Git, while `.env` files remain ignored.
- Curated skills were installed for the right agent, defaulting to OpenCode unless the user chose another agent, including the `dmno-dev/varlock` skill.
- `AGENTS.md` exists and contains the `## Repo Workspace Defaults` section, including the `### Resource Limits For Heavy Commands` subsection covering `systemd-run` caps, `/usr/bin/time -v` logging to `.tmp/logs/`, background execution with a monitor sub-agent, flushed progress output from our own scripts, and tail-only log reading.
- Existing `AGENTS.md` content outside `## Repo Workspace Defaults` was preserved.
- No existing file content, config key, array item, or comment was removed without explicit user approval.
- For an existing working repo, an installation plan (clean adds / merges / conflicts) was presented and approved before any changes beyond inspection; conflict-bucket items were left untouched unless the user explicitly opted in.
