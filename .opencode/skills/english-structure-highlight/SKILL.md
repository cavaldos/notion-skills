---
name: english-structure-highlight
description: Apply consistent color-coded highlighting to English sentence structure - main subject, main verb, object/complement, relative clause - via rich-text annotations in Notion pages/tables or plain markdown. Use when asked to highlight, color-code, or format English sentences by grammar role, e.g. "highlight cấu trúc câu", "format lại đoạn văn tiếng Anh", "tô màu chủ ngữ / động từ / tân ngữ", "mệnh đề quan hệ màu xám". Touches English text only; never edits wording.
---

# Highlight English Sentence Structure

Color-code the grammatical skeleton of English sentences so that anyone can read the S-V-O structure at a glance. Built for TOEIC/SW study pages in Notion but works on any English prose.

## Core Rule

- **Preserve text verbatim.** This skill changes *annotations only* (color, bold, italic, underline). Never add, remove, reword, or fix typos in the target text unless explicitly asked.
- **One legend for all sentences.** Every sentence in the document must follow the exact same mapping from grammar role to style. Consistency beats completeness.
- **English only by default.** Do not annotate Vietnamese translations, plans, or outlines in the same table.

## Default Legend

Use this when the user does not specify colors. Always state the legend before applying it; let the user override any entry.

| Grammar role | Annotation (`annotations` values) |
| --- | --- |
| Main subject (chủ ngữ chính) | `color: "yellow"` |
| Main verb (động từ chính) | `color: "red"`, `bold: true` |
| Object / complement (tân ngữ / bổ ngữ) | `color: "blue"`, `italic: true` |
| Relative clause (mệnh đề quan hệ) | `color: "gray"` |
| Everything else (transitions, adverbials, prepositional phrases…) | all defaults |

Notes:

- Notion renders the **yellow font** faintly on white backgrounds. If readability matters, offer `yellow_background` (highlighter-pen effect, black text) as an alternative before applying.
- Red + bold carries the strongest visual weight, which is why the verb uses it by default.

## Grammar Classification Rules

- **Main subject**: the full noun phrase of a finite clause, including determiners, adjectives, and post-modifiers — e.g. `a retail company in my city`, `salary alone`, `Simple recognition and reward, flexible working arrangements, ...` (compound subjects are marked whole).
- **Main verb**: the finite verb including auxiliaries — `is`, `should ensure`, `can provide`, `has been dropped`. In compound predicates mark each finite verb (`stayed`, `became`). Imperatives count (`Take`).
- **Object slot**: direct object, indirect object, **and** the complement of linking verbs (`is`, `became`, `seem`). Mark the entire slot content, including:
  - Noun clauses filling the slot: `is` + `that employees stay when they see...` → blue as one segment.
  - Two objects in a row (`gave it's staff a fifteen percent raise`) → both blue.
- **Relative clause**: `who / whom / whose / which / that` (and reduced forms) modifying a noun → gray, wherever it appears, even nested inside another element. Set off by commas or not — same treatment.
- **NOT relative clauses** (leave default): adverbial clauses introduced by `when, because, if, so that, whereas, after, while`; transition words (`However, For instance, Moreover`); prepositional phrases; infinitive phrases (`to stay`); bare-infinitive complements (`rise sharply`); object complements (`feel respected as individuals`).
- **Compound sentences**: annotate S-V-O independently per finite clause, splitting at `, and`, `;`, `whereas`, etc.

## Notion Implementation

### Reading

1. `notion_read_page` with `content_format: "markdown"` → locate the target table block ID and its row block IDs.
2. `notion_retrieve_block` (`format: "json"`) on **each row** you will modify → capture the exact current cells. On TOEIC SW pages the column order is `Outline | Plan | English | self-written | Vietnamese`; the annotated column is usually `self-written` (index 3).

### Updating

3. Use `notion_update_block` with payload shape:

```json
{
  "type": "table_row",
  "table_row": { "cells": [ [/*cell0*/], [/*cell1*/], /*...one flat array per cell*/ ] }
}
```

Hard-won pitfalls — do not skip:

- Each cell must be a **flat** array of rich_text segments. Double-nesting a cell as `[[{...}]]` fails with `400 validation_error: body.table_row.cells[0][0] should be an object`. This is the most common failure mode.
- Segment shape: `{"type":"text","text":{"content":"..."},"annotations":{"bold":false,"italic":false,"strikethrough":false,"underline":false,"code":false,"color":"..."}}`. Specify every annotation flag explicitly — omitted flags may reset to defaults.
- Valid `color` values: `default, gray, brown, orange, yellow, green, blue, purple, pink, red` plus `<name>_background` variants.
- The API **replaces the whole row**. Re-send all five cells; copy untouched cells (Outline, Plan, English model, Vietnamese) byte-for-byte from the retrieved JSON.
- Batch at most 2–3 row updates per message. Larger parallel payloads risk truncation → `JSON Parse error: Unterminated string`. Retry truncated rows individually.
- Verification: re-read the page afterwards and spot-check one row.

### Segment-building checklist

Before sending an update, verify programmatically or by eye:

1. Concatenating every segment's `text.content` reproduces the original cell string exactly — same spaces, punctuation, curly vs straight apostrophes, trailing spaces, and intentional typos.
2. Leading/trailing spaces live inside adjacent segments; a dropped space between two colored segments merges words together visually.
3. No segment has empty content except deliberate single-space spacers.

## Workflow

1. **Confirm legend** — propose the default legend (or the user's custom colors) in one short table; proceed once confirmed.
2. **Locate targets** — read the page; identify table rows or blocks holding the English text.
3. **Retrieve exact JSON** for every row to modify.
4. **Analyze** each sentence into roles per the classification rules above; produce a segmentation plan.
5. **Build segment arrays**, run the checklist.
6. **Update rows** in small batches; verify by reading back; summarize what was applied.

## Worked Example

Text (typos preserved): `When employees see tat their effort is properly rewarded, they have no financial reason to look for another job.`

Segments:

```
[default ] "When employees see tat their effort is properly rewarded,"
[yellow  ] "they"
[red+bold] " have"
[blue+it ] " no financial reason"
[default ] " to look for another job."
```

Full annotation presets and a complete ready-to-paste segment array: see `references/annotation-presets.json`.

## Constraints

- Formatting skill, not editing skill — zero wording changes; list spotted typos at the end of your reply instead of fixing them silently.
- Never touch columns/languages outside the requested target.
- If the user asks for different colors mid-task, rebuild affected rows with the new legend applied uniformly — never mix legends within one document.
