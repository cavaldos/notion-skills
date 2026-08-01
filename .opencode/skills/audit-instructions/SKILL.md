---
name: audit-instructions
description: Tighten and reorganize an agent's instruction page so it's lean, clear, and easy to maintain. Use when asked to audit instructions, review an AGENTS.md or system prompt, or improve agent documentation.
---

# Audit Instructions

Review an instruction document (e.g., agent instructions, AGENTS.md) and make it lean, clear, and maintainable.

## When to use

- Tighten and reorganize an agent's instruction page so it's lean, clear, and easy to maintain. Use when asked to audit instructions, review an AGENTS.md or system prompt, or improve agent documentation.

## Workflow

1. Read the full instruction page and map its current structure.
2. Identify redundancy, contradictions, and outdated or dead content.
3. Check for ambiguity: can a reader act on each instruction?
4. Reorganize into a logical hierarchy: priorities, rules, conventions, references.
5. Rewrite verbose sections to be concise without losing meaning.
6. Preserve all binding rules (P0/P1 priorities) verbatim or cleaner.
7. Produce the revised page plus a change summary.

## Output format

A tightened instruction page and a summary of changes made.

## Constraints

- Do not drop any rule with binding priority - reorganize, never delete meaning.
- Keep the document scannable: short sections, clear headings.
