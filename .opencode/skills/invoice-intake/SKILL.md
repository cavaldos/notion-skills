---
name: invoice-intake
description: Parse an invoice into a clean, structured database row. Use when asked to process an invoice, extract invoice data, or parse invoice details.
---

# Invoice Intake

Extract invoice fields into a clean, structured record.

## When to use

- Parse an invoice into a clean, structured database row. Use when asked to process an invoice, extract invoice data, or parse invoice details.

## Workflow

1. Read the invoice and identify standard fields: vendor, invoice number, date, due date, line items, totals, tax.
2. Extract each field accurately, preserving amounts as-is.
3. Normalize formats: dates, currency, names.
4. Handle edge cases: multiple pages, currency symbols, tax splits.
5. Flag missing or inconsistent fields.

## Output format

A structured invoice record with all extracted fields.

## Constraints

- Never round or adjust amounts - preserve exact values.
- Flag anything unclear instead of guessing.
