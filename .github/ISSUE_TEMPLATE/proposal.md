---
name: Engineering rule proposal
about: Propose a rule/standard to bake into the scaffolding templates
title: "area/rule-id: <imperative one-liner>"
labels: ["state:proposal"]
---

<!--
Add the remaining labels by hand (or let the seed script do it):
  area:<architecture|standards|infra|impl/...>   enforcer:<ast-grep|import-linter|ruff|pytest|kube-linter|script|llm>
  priority:<high|medium|low>
The issue NUMBER is the stable id. Priority/state are labels, never the number.
-->

## Summary
<!-- One sentence: what this rule mandates. -->

## Rule / decision
<!-- The precise, testable statement of the rule. -->

## Enforcement
- **Enforcer:** <ast-grep | import-linter | ruff | pytest | kube-linter | script | llm>
- **Tier:** <deterministic | hybrid | judgment>  <!-- derived: only llm = judgment; llm+tool = hybrid; no llm = deterministic -->
- **Applies to:** <all | fastapi | nextjs | prefect | asr | k8s | ...>

<!-- The ACTUAL change/config that implements the rule: the pyproject.toml block,
     import-linter contract, ast-grep YAML, kube-linter check, shell snippet, etc. -->
```toml
# e.g. the block added to pyproject.toml
```

## Reasoning
<!-- Why. Semantic anchor if any; cross-repo evidence; what problem it prevents. -->

## Conflicts & risks
<!-- Collisions with existing conventions (esp. respect-local-repo), false positives,
     overlap/duplication with other proposals. -->

## Blast radius
<!-- Scope of impact: which repos/layers/files; expected noise; CI vs pre-commit;
     error vs warning. How disruptive is turning this on? -->

## Migration (existing repos)
<!-- How to adopt where the rule is NOT yet satisfied:
     opt-in per repo, grandfather (ignore_imports / baseline), codemod, phased rollout,
     or "new repos only". import-linter & other whole-repo checks MUST address this. -->

## References
<!-- Provenance file, related proposals (#ids), semantic anchor links. -->
