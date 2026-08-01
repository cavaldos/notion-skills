---
name: normalize-currency-to-usd
description: Convert imported values into USD for consistent reporting. Use when asked to convert currency to USD, normalize currency, or make figures comparable across currencies.
---

# Normalize Currency to USD

Convert values in various currencies into USD consistently.

## When to use

- Convert imported values into USD for consistent reporting. Use when asked to convert currency to USD, normalize currency, or make figures comparable across currencies.

## Workflow

1. Identify all currency values and their original currencies.
2. Use a clear, stated conversion rate per currency (user-provided or current reference).
3. Convert each value, preserving precision.
4. Keep the original value alongside for traceability.
5. Flag any values with ambiguous or unknown currency.

## Output format

Values converted to USD with original values retained and rates stated.

## Constraints

- State the conversion rates used and the date.
- Never silently round; preserve cents/precision.
