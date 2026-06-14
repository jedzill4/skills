# jedzill4-skills

Personal agent skills for OpenCode-first development.

Most engineering workflow skills I use come from Matt Pocock's [`skills`](https://github.com/mattpocock/skills). This repo intentionally does not vendor those skills; it only contains my own local additions.

## Install

Default agent target is OpenCode. Install selected upstream skills from Matt Pocock:

```bash
npx skills add mattpocock/skills --agent opencode --yes --skill diagnose grill-with-docs triage improve-codebase-architecture tdd to-issues to-prd zoom-out prototype grill-me handoff write-a-skill
```

Then install my local skills from this repo:

```bash
npx skills add jedzill4/skills --agent opencode --yes --skill setup-repo journalist
```

If installing my local skills from a checkout, run from this repo:

```bash
npx skills add . --agent opencode --yes --skill setup-repo journalist --full-depth
```

Use `--agent claude-code` or `--agent codex` instead only when that is the agent you actually use.

## Upstream Skills From Matt Pocock

- `diagnose`, `tdd` — engineering quality workflows.
- `to-prd`, `to-issues`, `triage` — planning and issue workflows.
- `prototype` — throwaway code/UI prototyping.
- `improve-codebase-architecture`, `zoom-out` — architecture and system understanding workflows.
- `grill-me`, `grill-with-docs`, `handoff`, `write-a-skill` — meta/collaboration workflows.

## Local Skills

- `setup-repo` — repo workspace defaults, OpenCode config, gitignore, AGENTS.md, and optional prek hooks.
- `journalist` — local daily session journals under `.journals/`.
