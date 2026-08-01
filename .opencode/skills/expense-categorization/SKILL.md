---
name: expense-categorization
description: Automatically tag transactions to the right categories or budgets. Use when asked to categorize expenses, tag transactions, or sort spending into budget categories.
---

# Expense Categorization

Assign each transaction to the right expense category or budget.

## When to use

- Automatically tag transactions to the right categories or budgets. Use when asked to categorize expenses, tag transactions, or sort spending into budget categories.

## Workflow

1. Define the category set (provided or standard: food, rent, transport...).
2. For each transaction, infer the category from merchant and description.
3. Apply consistent rules for ambiguous cases (subscriptions, transfers).
4. Flag transactions that cannot be confidently categorized.
5. Present a categorized list with totals per category.

## Output format

A categorized transaction list with category totals and flagged unknowns.

## Constraints

- Do not guess on ambiguous entries - flag them.
- Keep consistent rules across all transactions.
