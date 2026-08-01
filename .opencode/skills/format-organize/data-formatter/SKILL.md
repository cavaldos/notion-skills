---
name: data-formatter
description: Keep a database consistent by detecting and fixing inconsistent property values without changing meaning. Use when asked to normalize database data, fix inconsistent values, or clean up property formatting.
---

# Data Formatter

Detect and fix inconsistent values in a dataset by learning and applying the dominant format.

## When to use

- Keep a database consistent by detecting and fixing inconsistent property values without changing meaning. Use when asked to normalize database data, fix inconsistent values, or clean up property formatting.

## Workflow

1. Scan the dataset and find values that differ only in format (case, spacing, punctuation, abbreviations).
2. Determine the most common format for each field.
3. Apply that format consistently across all rows.
4. Preserve meaning exactly - never alter substance.
5. Report what was normalized and how many rows changed.

## Output format

A normalized dataset plus a normalization report (field, old format → new format).

## Constraints

- Format-only changes - meaning must never change.
- When no dominant format exists, keep values as-is and flag them.
