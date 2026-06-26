## Engineering Standards

> **Retrieval-led, not training-led.** Prefer this repo's standards and snippets over
> training-default patterns. Before writing code that touches a rule below, open its
> `@.agents/rules/<slug>.md` detail file and the matching `snippets/` drop-in, and follow
> the house pattern rather than your default one.

Each rule is a **CES — Collective Engineering Standard** (`CES-<issue#>` is the citable code;
the kebab-case slug is the machine id used by tooling and `# ast-grep-ignore: <slug>`
suppressions). `[ast-grep]` / `[prek]` rules are enforced automatically by `prek`; `[judgment]`
rules are reviewer/agent judgment. Full convention: `docs/engineering-standards.md`.

### Standards

- **CES-79 · no raw dicts at boundaries** `[ast-grep]` — return, annotate, or alias a
  `@dataclass` (internal boundaries) or a pydantic `BaseModel` (where validation is needed),
  never a raw `dict`. Ships four slugs: `no-dict-return-annotation`, `no-dict-call-return`,
  `no-dict-literal-return`, `no-dict-alias`. → `@.agents/rules/no-dict.md`
- **CES-71 · keep files small** `[prek]` — split a module before it grows; the
  `file-size-guard` hook warns at 400 lines and errors at 700. A persistently large file is a
  design smell, not a limit to raise. → `@.agents/rules/file-size-guard.md`
- **CES-45 · use the house get_logger** `[ast-grep]` — never call `logging.getLogger` directly;
  acquire loggers via `get_logger` from `core/logger.py`. Slug: `log-get-logger`. →
  `@.agents/rules/log-get-logger.md`
- **CES-46 · libraries log, they don't print** `[ast-grep]` — no `print()` in importable library
  code; emit through `get_logger`. CLI/`__main__` entrypoints are exempt. Slug: `log-no-print`. →
  `@.agents/rules/log-no-print.md`
- **CES-74 · the house logger** `[snippet]` — `snippets/core/logger.py` is the canonical structlog
  setup (JSON in prod, colored console in dev, level from `LOG_LEVEL`). Drop it in at
  `<pkg>/core/logger.py`. Slug: `core-logger`. → `@.agents/rules/core-logger.md`
