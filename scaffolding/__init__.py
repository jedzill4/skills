"""scaffolding — deterministic, clean-adds-only repo bootstrap CLI.

The CLI is the deterministic engine for repo bootstrap; an agent drives it for
the merge/judgment cases. It never edits, merges, or overwrites existing files:
existing targets are deferred to the agentic guide.
"""

__version__ = "0.1.0"
