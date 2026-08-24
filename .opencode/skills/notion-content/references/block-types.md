# Notion Block Types — Full Reference

Companion to `notion-content/SKILL.md`. Source: https://developers.notion.com/reference/block
(API version `2026-03-11`.)

## Common fields on every block

| Field | Type | Notes |
| --- | --- | --- |
| `object` | string | Always `"block"` |
| `id` | UUIDv4 | Block identifier |
| `parent` | object | Parent object (page_id / block_id / database_id / workspace) |
| `type` | enum | See list below |
| `created_time`, `last_edited_time` | ISO 8601 | Timestamps |
| `created_by`, `last_edited_by` | partial user | |
| `in_trash` | boolean | Use this (NOT deprecated `archived`) to check/restore/trash |
| `has_children` | boolean | If true, fetch children via Retrieve block children |
| `{type}` | object | Type-specific payload |

## Block types that support children

bulleted_list_item, callout, child_database, child_page, column, heading_1–4 (only when
`is_toggleable: true`), meeting_notes (transcription), numbered_list_item, paragraph, quote,
synced_block, table, template, to_do, toggle.

## Type-by-type notes

### paragraph → plain text
`rich_text`. Supports children. Line breaks inside: `<br>` in markdown, or multiple rich_text runs.

### heading_1..4 → `#`..`####`
`rich_text`, `color`, `is_toggleable` (true = toggle heading that can hold children).

### bulleted_list_item → `- item`
`rich_text`, `color`, `children`.

### numbered_list_item → `1. item`
Same shape as bulleted; numbering is automatic per contiguous run.

### to_do → `- [ ]` / `- [x]`
`rich_text`, `checked` (boolean), `color`, `children`.

### toggle → `<details>/<summary>`
`rich_text`, `color`; children hold the hidden content.

### quote → `> quote`
`rich_text`, `color`, supports children.

### callout → `<callout>` tag
`rich_text`, `icon` (emoji / custom emoji / native icon / file), `color`.
Example icon: `{"type": "emojis", "emoji": "⭐"}` shape varies by icon kind.

### divider → `---`
Empty payload (`"divider": {}`).

### code → fenced code block with language
`caption`, `rich_text`, `language`. Language is an exact enum string:
abap, arduino, bash, basic, c, clojure, coffeescript, c++, c#, css, dart, diff, docker, elixir,
elm, erlang, flow, fortran, f#, gherkin, glsl, go, graphql, groovy, haskell, html, java,
javascript, json, julia, kotlin, latex, less, lisp, livescript, lua, makefile, markdown, markup,
matlab, mermaid, nix, objective-c, ocaml, pascal, perl, php, plain text, powershell, prolog,
protobuf, python, r, reason, ruby, rust, sass, scala, scheme, scss, shell, sql, swift,
typescript, vb.net, verilog, vhdl, visual basic, webassembly, xml, yaml, java/c/c++/c#.

### equation → `$$ expression $$`
KaTeX-compatible `expression` string. Inline equations are rich_text equation objects inside
paragraphs.

### table → `<table><tr><td>…</td></tr></table>`
Parent of `table_row` blocks.
- `table_width`: column count — **settable only at creation**; update calls fail.
- `has_column_header`: first row styled as header.
- `has_row_header`: first column styled as header.
- At creation include ≥ 1 `table_row`; each row's `cells` array length must equal `table_width`.
- Each cell is an array of rich_text objects.

### image / video / audio / pdf / file
Markdown: `![caption](url)` for images; `<file src="url">caption</file>`,
`<video src="url">…</video>`, `<audio src="url">…</audio>`, `<pdf src="url">…</pdf>` otherwise.
Payload: `caption` + one of `file` (Notion-hosted, temporary signed URL with expiry),
`external` ({url}), `file_upload` ({id} — attach only; response returns type `file`).
Audio external formats: mp3, wav, ogg, oga, m4a. Never cache signed URLs — refetch.

### child_page → `<page url="...">title</page>`
Payload `{title}`. Create/update via page endpoints, not append-blocks.

### child_database → `<database url="...">title</database>`
Payload `{title}` (plain text). Create/update via Create/Update a database endpoints with the
parent page ID.

### bookmark / embed / link_preview → `<unknown .../>` in markdown
- bookmark: `caption` + `url`.
- embed: `url` (may be a temporary signed link for uploaded files).
- link_preview: `url`.
These render as `<unknown url="..." alt="bookmark"/>` etc. in markdown output.

### breadcrumb → `<unknown .../>`
Empty payload. Navigation breadcrumbs.

### synced_block → `<synced_block>`
Original: `synced_from: null` + `children` (content mirrored to duplicates).
Duplicate: `synced_from: {type: "block_id", block_id: "<original id>"}`.
Create originals before duplicates. **Content updates are not supported by the API.**

### column_list / column → `<columns>` / `<column>`
Both payloads empty except optional `column.width_ratio` (0–1; ratios should sum to 1).
Creation rules: column_list needs ≥ 2 columns; each column ≥ 1 child; columns append only to
column_lists. Reading requires nested calls: page children → find column_list → its column
children → each column's content children.

### table_of_contents → `<table_of_contents/>`

### tab
Payload empty. Only paragraph children allowed; each paragraph child = one tab (its rich_text =
label, its icon = tab icon, its children = tab content).

### template → `<unknown .../>`
DEPRECATED — creation unsupported since March 2023. Payload: `rich_text` + `children`.

### meeting_notes (renamed from transcription in 2026-03-11) → `<meeting-notes>`
Represents AI meeting notes: metadata + pointers to child content.
- `status` lifecycle: transcription_not_started, transcription_paused, transcription_in_progress,
  transcription_failed, summary_in_progress, notes_ready.
- `children` pointers: `summary_block_id`, `notes_block_id`, `transcript_block_id` (optional UUIDs).
Transcript text is excluded from markdown reads unless `include_transcript=true`, and is ALWAYS
invisible to markdown updates.

### unsupported
`type: "unsupported"` with payload `unsupported.block_type` — a plain informational string
(e.g. form, button, drive). Not an enum; new values may appear at any time. Do not rely on a
fixed set.

## Color enum (shared by most text blocks)

default, gray, brown, orange, yellow, green, blue, purple, pink, red — plus the same names with
`_background` suffix. `"default"` means untouched styling.
