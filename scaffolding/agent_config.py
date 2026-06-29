"""Per-agent config emission (the ``agent-config`` component).

opencode + codex follow the shared ``.agents``/``AGENTS.md`` standard; claude-code
is the exception (``.claude/`` + ``CLAUDE.md``) and is bridged with symlinks. This
module owns the agent-target resolution, the multi-select decision, and the
per-agent op handlers. Imports flow one way: ``components`` -> ``agent_config`` ->
``ops``/``plan``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffolding.ops import symlink_if_absent, write_if_absent
from scaffolding.plan import Agent, Decision, Disposition, Op
from scaffolding.templates_registry import template_text

if TYPE_CHECKING:
    from scaffolding.components import Context

AGENT_CHOICES = [a.value for a in Agent]
# Standard skill/instruction layout (.agents/skills + AGENTS.md) read natively by
# opencode + codex. Claude diverges, so it is bridged into .claude via symlinks.
AGENTS_SKILLS_DIR = ".agents/skills"
# Codex has no repo-local deny-list; surface how to protect secrets with it.
CODEX_PROTECTION_NOTICE = (
    "codex: no repo-local deny-list — secrets protected via (1) varlock "
    "(.env.schema committed, .env* gitignored; use `varlock load`, never `cat .env`), "
    "(2) AGENTS.md file-access rules (read natively by codex), (3) the prek leak-scan "
    'pre-commit hook, (4) harden ~/.codex/config.toml: sandbox_mode="workspace-write", '
    'approval_policy="on-request" (developers.openai.com/codex/config-reference). '
    "No live redaction equivalent to the opencode-varlock plugin."
)


def selected_agents(ctx: Context) -> list[Agent]:
    """Resolve agent targets for this run: the user's decision, else settings."""
    settings_agents = [Agent(a) for a in ctx.settings.agents if a in AGENT_CHOICES]
    raw = ctx.decisions.agents or settings_agents
    return list(dict.fromkeys(raw)) or [Agent.OPENCODE]


def register_agents_decision(ctx: Context) -> None:
    """Register the Tier-2 multi-select agent-target decision (idempotent)."""
    default = ",".join(a.value for a in selected_agents(ctx))
    ctx.add_decision(
        Decision(2, "agents", "Which agent target(s)? (opencode/claude-code/codex)", default)
    )


def _agent_ops_opencode(ctx: Context) -> list[Op]:
    return [
        write_if_absent(
            "agent-config",
            ctx.root / "opencode.jsonc",
            template_text("opencode-template.jsonc"),
            "opencode.jsonc",
            ctx.guide_url,
        )
    ]


def _agent_ops_claude(ctx: Context) -> list[Op]:
    # Claude is the odd agent out: it reads CLAUDE.md + .claude/skills rather than the
    # AGENTS.md / .agents standard, so bridge both with symlinks plus its own deny-list.
    return [
        write_if_absent(
            "agent-config",
            ctx.root / ".claude" / "settings.json",
            template_text("claude-settings-template.json"),
            ".claude/settings.json",
            ctx.guide_url,
        ),
        symlink_if_absent(
            "agent-config", ctx.root / "CLAUDE.md", "AGENTS.md", "CLAUDE.md", ctx.guide_url
        ),
        symlink_if_absent(
            "agent-config",
            ctx.root / ".claude" / "skills",
            "../.agents/skills",
            ".claude/skills",
            ctx.guide_url,
        ),
    ]


def _agent_ops_codex(_ctx: Context) -> list[Op]:
    return [
        Op(
            "agent-config",
            "noop",
            "codex secret protection",
            Disposition.SKIP,
            detail=CODEX_PROTECTION_NOTICE,
        )
    ]


def plan_agent_config(ctx: Context) -> list[Op]:
    register_agents_decision(ctx)
    handlers = {
        Agent.OPENCODE: _agent_ops_opencode,
        Agent.CLAUDE_CODE: _agent_ops_claude,
        Agent.CODEX: _agent_ops_codex,
    }
    ops: list[Op] = []
    for agent in selected_agents(ctx):
        ops += handlers[agent](ctx)
    return ops
