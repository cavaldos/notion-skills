---
name: build-a-skill
description: A guided builder that walks through creating a well-scoped new AI skill. Use when asked to create a new skill, write a SKILL.md, or build a skill for an agent.
---

# Build a Skill

Guide the creation of a well-scoped, effective AI agent skill from scratch.

## When to use

- A guided builder that walks through creating a well-scoped new AI skill. Use when asked to create a new skill, write a SKILL.md, or build a skill for an agent.

## Workflow

1. Clarify the skill's single purpose: what task does it make reliably better?
2. Define triggers: when should the skill activate? List concrete user phrases.
3. Write the SKILL.md frontmatter: name (lowercase, hyphenated, matches folder) and description (what + when, third person).
4. Structure the body: purpose, when to use, workflow steps, output format, constraints.
5. Keep the skill focused and scannable; add examples where helpful.
6. Place it at .opencode/skills/<name>/SKILL.md and verify the loader sees it.

## Output format

A complete, well-scoped SKILL.md file plus placement guidance.

## Constraints

- One skill = one job. If the scope grows, split it.
- Description must front-load trigger keywords to surface in discovery.
