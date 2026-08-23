---
name: english-structure-highlight
description: Apply consistent color-coded highlighting to English sentence structure - main subject, main verb, object/complement, relative clause, comparative structure, object complement, plus collocation overlay - via rich-text annotations in Notion pages/tables or plain markdown. Use when asked to highlight, color-code, or format English sentences by grammar role, e.g. "highlight cấu trúc câu", "format lại đoạn văn tiếng Anh", "tô màu chủ ngữ / động từ / tân ngữ", "mệnh đề quan hệ màu xám", "tô so sánh / collocation". Touches English text only; never edits wording.
---

# Highlight English Sentence Structure

Color-code the grammatical skeleton of English sentences so that anyone can read the S-V-O structure at a glance. Built for TOEIC/SW study pages in Notion but works on any English prose.

## Core Rule

- **Preserve text verbatim.** This skill changes *annotations only* (color, bold, italic, underline). Never add, remove, reword, or fix typos in the target text unless explicitly asked.
- **One legend for all sentences.** Every sentence in the document must follow the exact same mapping from grammar role to style. Consistency beats completeness.
- **English only by default.** Do not annotate Vietnamese translations, plans, or outlines in the same table.
- **Default means untouched.** Text outside the seven legend layers keeps Notion's pure default state — every annotation flag `false`, `color: "default"` (the "white" text). Never restyle default territory: transitions, adverbial clauses, prepositional phrases, purpose infinitives, etc. receive zero formatting, including overlays.

## Default Legend

Use this when the user does not specify colors. Always state the legend before applying it; let the user override any entry.

| Grammar role | Annotation (`annotations` values) |
| --- | --- |
| Main subject (chủ ngữ chính) | `color: "yellow"` |
| Main verb (động từ chính) | `color: "red"`, `bold: true` |
| Object / complement (tân ngữ / bổ ngữ chủ) | `color: "blue"`, `italic: true` |
| Relative clause (mệnh đề quan hệ) | `color: "gray"` |
| Comparative structure (cấu trúc so sánh) | `color: "pink"` |
| Object complement (bổ ngữ cho tân ngữ) | `color: "blue"`, `underline: true` |
| Collocation (overlay) | merge `italic: true` into the segment's existing annotations — keep the role's color |
| Everything else (transitions, adverbials, prepositional phrases…) | all defaults |

Notes:

- Notion renders the **yellow font** faintly on white backgrounds. If readability matters, offer `yellow_background` (highlighter-pen effect, black text) as an alternative before applying.
- Red + bold carries the strongest visual weight, which is why the verb uses it by default.
- The legend is capped at **7 layers**. Do not add more colors without an explicit user request — past ~7 the page becomes unreadable and defeats the purpose of at-a-glance structure reading.

## Grammar Classification Rules

- **Main subject**: the full noun phrase of a finite clause, including determiners, adjectives, and post-modifiers — e.g. `a retail company in my city`, `salary alone`, `Simple recognition and reward, flexible working arrangements, ...` (compound subjects are marked whole).
- **Main verb**: the finite verb including auxiliaries — `is`, `should ensure`, `can provide`, `has been dropped`. In compound predicates mark each finite verb (`stayed`, `became`). Imperatives count (`Take`).
- **Object slot**: direct object, indirect object, **and** the complement of linking verbs (`is`, `became`, `seem`). Mark the entire slot content, including:
  - Noun clauses filling the slot: `is` + `that employees stay when they see...` → blue as one segment.
  - Two objects in a row (`gave it's staff a fifteen percent raise`) → both blue.
- **Relative clause**: `who / whom / whose / which / that` (and reduced forms) modifying a noun → gray, wherever it appears, even nested inside another element. Set off by commas or not — same treatment. Sentential relatives (`, which improves...` commenting on the whole clause) are gray too.
- **Comparative structure** → pink: comparative/superlative forms (`better`, `more destinations`, `far more calmly`, `the best`) and comparison connectors (`than`, `rather than`, `compared with/to`, `as ... as`). Mark the comparative word or phrase itself plus its connector when adjacent; do not color whole sentences just because they contain a comparison. Precedence: when the comparative form itself fills the object/complement slot (`is the better choice`), the blue role color wins — pink is reserved for comparatives in unmarked territory (`far more calmly`, `rather than waiting twelve months`).
- **Object complement** → blue + underline: the element that completes the meaning of the object — bare infinitive after causatives/perception verbs (`let pressure build up`, `help them stay productive`, `make people feel respected`), adjectives/participles after linking-intransitive verbs (`come back refreshed`, `feel exhausted`). Direct objects of those same verbs stay plain blue italic (`pressure`, `them`); only the completing element gets the underline.
- **Collocation overlay** → italic, no dedicated color: natural multi-word chunks (`take time off`, `reduce stress`, `save money`, `paid time off`, `work-life balance`, `build up`). This is an **overlay layer**, applied after all role colors:
  1. Take each collocation chunk's existing segment annotations and set `italic: true`; keep the role's color unchanged.
  2. The overlay lands **only on already-colored object/complement segments** (blue family). A collocation chunk lying in default territory (inside adverbials, prepositional phrases, transitions) is left **completely untouched** — default text stays pure default per the Core Rule.
  3. Never italicize subjects, verbs, or relative clauses *solely* because they belong to a chunk — mark only chunks whose head is an object/complement. Grammar roles always win over the vocabulary layer.
- **NOT relative clauses** (leave default unless another rule applies): adverbial clauses introduced by `when, because, if, so that, whereas, after, while`; transition words (`However, For instance, Moreover`); prepositional phrases; purpose/catenative infinitive phrases (`to stay`, `to plan frequent short getaways`).
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

New-layer example A — object complement + collocation: `When employees take a long weekend every few months, they never let pressure build up to a breaking point.`

```
[default     ] "When employees take a long weekend every few months, "
[yellow      ] "they"
[default     ] " never "
[red+bold    ] "let"
[blue+italic ] " pressure"
[blue+underline] " build up"
[default     ] " to a breaking point."
```

New-layer example B — comparative connector in unmarked territory: `For these reasons, I will continue to plan frequent short getaways rather than waiting twelve months for a single trip.`

```
[default ] "For these reasons, "
[yellow  ] "I"
[red+bold] " will continue"
[default ] " to plan frequent short getaways "
[pink    ] "rather than waiting twelve months"
[default ] " for a single trip."
```

Full annotation presets and a complete ready-to-paste segment array: see `references/annotation-presets.json`.

## Constraints

- Formatting skill, not editing skill — zero wording changes; list spotted typos at the end of your reply instead of fixing them silently.
- Never touch columns/languages outside the requested target.
- If the user asks for different colors mid-task, rebuild affected rows with the new legend applied uniformly — never mix legends within one document.
