---
name: toeic-save-to-notion
description: Save a TOEIC essay to the user's Notion database with Outline | English | Vietnamese table format. Use after writing a TOEIC model essay when the user wants to save it to Notion, or when asked to save/update a TOEIC essay to Notion. Trigger when the user says "save essay to Notion", "save to Notion", "update Notion essay", or similar. Handles creating new pages, filling tables, and updating existing entries.
---

# Save TOEIC Essay to Notion

## Core Rule

This skill handles saving a completed TOEIC essay to the user's Notion "Toeic Essay Database". It should be called **after** the essay has been written using the `toeic-essay` skill.

## Prerequisites

- A completed TOEIC essay (English + Vietnamese translation)
- The essay topic/prompt
- Access to the Notion MCP tools

## Database Info

### "Toeic Essay Database" — compiled exam questions

- `data_source_id`: `3aaf312e-ab25-80d5-877a-000beaedbe1b` (legacy `database_id`: `3aaf312e-ab25-80f0-9ce2-e9b49be92fc0`)
- Properties:
  - `Name` (title): short topic title
  - `Subject` (rich_text): the full exam prompt
  - `Themes` (select): Workplace & working conditions, Career Choice & Career Path, Leadership & People Management, Business & Career Success, Education & Learning, Society government & community, Personal life hobbies mental health, Company/Service Characteristics
  - `Kind` (select): Agree / Disagree, Preference, (Advantages/Disadvantages), (Why/What), (3-choice)
  - `Keyword` (rich_text): key search terms
  - `Status` (status): "Not started" / "Done"

## Workflow

### Step 1 — Find the matching page

Search the Toeic Essay Database for a page whose `Subject` matches the prompt:

- Use `notion_API-post-search` with `query` = a distinctive phrase of the prompt, or
- Use `notion_API-query-data-source` on the database and match on the `Subject` property.

If a matching page exists → use it (fill its table, see Step 3). If not → create a new page (Step 2).

### Step 2 — Create a new page (only if no match)

`notion_API-post-page` with:

- `parent`: `{"type": "database_id", "database_id": "3aaf312e-ab25-80f0-9ce2-e9b49be92fc0"}`
- `properties`:
  - `Name` (title): short topic title, e.g. "Working from Home vs. Working at the Office"
  - `Subject` (rich_text): the full exam prompt
  - `Themes` (select): pick the matching theme
  - `Kind` (select): Agree / Disagree, Preference, (Advantages/Disadvantages), (Why/What), (3-choice)
  - `Keyword` (rich_text): key search terms
  - `Status` (status): "Not started"
- `children`: a callout block (💡) + a `table` block with `table_width: 3`, `has_column_header: true`, `has_row_header: true`, containing the header row (`Outline`, `English`, `Vietnamese`) and 5 empty rows (`Introduction`, `Body 1`, `Body 2`, `Body 3`, `Conclusion`).

### Step 3 — Fill the table

**Known limitation:** `notion_API-update-a-block` with `table_row` fails validation on this MCP server. Use this working pattern instead:

1. `notion_API-patch-block-children` on the table block id with 5 `table_row` children, each with 3 cells:
   - Cell 1 (Outline): `Introduction` / `Body 1` / `Body 2` / `Body 3` / `Conclusion`
   - Cell 2 (English): the English paragraph for that section
   - Cell 3 (Vietnamese): the Vietnamese translation of that section
2. `notion_API-get-block-children` on the table block to list existing rows, then `notion_API-delete-a-block` on every pre-existing empty row (keep the header row) so the table has exactly: header + 5 filled rows.

### Step 4 — Mark done

`notion_API-patch-page` with `properties: {"Status": {"status": {"name": "Done"}}}`.

### Step 5 — Local .md copy

Write the essay to `toeic-<slug>.md` in the workspace root (format: title, prompt, type/stance, essay, Vietnamese study notes with collocations and structures). Mention the file path in your reply.

## Table Format

The saved page should contain a table with this structure:

| Outline | English | Vietnamese |
| :--- | :--- | :--- |
| Introduction | [English intro paragraph] | [Vietnamese translation] |
| Body 1 | [English body paragraph 1] | [Vietnamese translation] |
| Body 2 | [English body paragraph 2] | [Vietnamese translation] |
| Body 3 | [English body paragraph 3 (if used)] | [Vietnamese translation] |
| Conclusion | [English conclusion paragraph] | [Vietnamese translation] |
