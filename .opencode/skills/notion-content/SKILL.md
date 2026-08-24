---
name: notion-content
description: Work with Notion page content correctly - read, create, and update pages using enhanced markdown or the block API. Covers every block type's markdown representation, safe update commands (update_content, replace_content, insert_content, replace_content_range), truncation and unknown-block recovery, async writes, and block-object constraints. Use whenever reading or writing structured content in Notion pages via API or MCP - e.g. "create a Notion page", "update this Notion page", "append content to Notion", "replace page content", "đọc trang Notion", "cập nhật trang Notion", "thêm nội dung vào Notion".
---

# Working with Notion Content (Blocks & Enhanced Markdown)

Canonical rules for any AI agent that reads, creates, or updates Notion page content.
Sources (official docs):

- Markdown API: https://developers.notion.com/guides/data-apis/working-with-markdown-content
- Block reference: https://developers.notion.com/reference/block

Deep details:

- `references/block-types.md` — every block type: JSON shape + markdown equivalent + gotchas
- `references/markdown-writes.md` — full spec of the 4 update commands, async tasks, error table

## Choose your surface first

| Situation | Surface |
| --- | --- |
| Read a whole page, create a whole page, bulk rewrite, targeted text edits | **Markdown API** (default for agents) |
| Move/reorder/delete one specific block, change color/icon/annotations, paginate huge pages | **Block API** |
| A block appears as `<unknown>` in markdown output | **Block API** (markdown cannot round-trip it) |

Rule of thumb: **think in markdown, fall back to blocks.**

## Golden rules (never violate)

1. **`\n` starts a new block; `<br>` is a line break inside one block.**
   `"# Title\nParagraph"` = heading + paragraph. Literal typed `\n` does NOT count as a newline.
2. **First `# h1` becomes the page title** when `properties.title` is omitted on create.
3. **`old_str` must match exactly once** (case-sensitive). Multiple matches fail with
   `validation_error` unless you set `replace_all_matches: true`.
4. **Updates refuse to delete child pages/databases** unless you pass
   `allow_deleting_content: true`. Read the validation error listing the affected items first;
   confirm, then opt in deliberately.
5. **File/media URLs are pre-signed and expire quickly.** Never cache them; refetch the block.
6. **`table_width` is immutable** — settable only when the table is first created.
7. **Meeting-note transcripts are invisible to updates**, even if read with
   `include_transcript=true`. Selections spanning transcript text always `validation_error`.
8. **Always check `truncated` and `unknown_block_ids` on every markdown read** before editing -
   you may be looking at an incomplete page (~20k-block record limit).
9. **Synced-block content cannot be updated through the API.**
10. **`archived` is deprecated** — use `in_trash` on block objects.
11. **Match IDs to the right endpoint type:** database IDs are rejected by page endpoints with
    `validation_error`; use the matching API per record type.

## Enhanced markdown cheat sheet (block ⇄ markdown)

| Block type | Markdown |
| --- | --- |
| Paragraph | plain text |
| Heading 1–4 | `#` / `##` / `###` / `####` |
| Bulleted list item | `- item` |
| Numbered list item | `1. item` |
| To do | `- [ ]` unchecked, `- [x]` checked |
| Toggle | `<details>` / `<summary>` |
| Quote | `> quote` |
| Callout | `<callout>` tag |
| Divider | `---` |
| Code | fenced code block with language |
| Equation | `$$ expression $$` |
| Table | `<table>` with `<tr>` / `<td>` |
| Image | `![caption](url)` |
| File / Video / Audio / PDF | `<file src="url">caption</file>` (same pattern per type) |
| Child page | `<page url="...">title</page>` |
| Child database | `<database url="...">title</database>` |
| Synced block | `<synced_block>` … content … |
| Column list / column | `<columns>` / `<column>` |
| Table of contents | `<table_of_contents/>` |
| Meeting notes | `<meeting-notes>` |

Adjacent top-level blocks are separated by a single `\n` in reads; writes accept the same format.

### Unsupported in markdown

Bookmark, Embed, Link preview, Breadcrumb, Template render as
`<unknown url="..." alt="block_type"/>` (`url` links into Notion, `alt` names the original type).
Inspect or modify them via the Block API instead.

## Reading a page as markdown

Endpoint: `GET /v1/pages/{page_id}/markdown`, optional query `include_transcript=true`.
Requires `read_content` capability.

Response shape:

```json
{
  "object": "page_markdown",
  "id": "page-uuid",
  "markdown": "# Meeting Notes\nDiscussed roadmap.\n<unknown url=\"https://notion.com/abc#def\"/>",
  "truncated": true,
  "unknown_block_ids": ["def456-with-dashes-uuid"]
}
```

Recovery loop for large or partially-shared pages - fetch each unknown ID through the same endpoint:

```
resp = GET /pages/{page_id}/markdown
all  = resp.markdown
for id in resp.unknown_block_ids:
    sub = GET /pages/{id}/markdown      # subtree if truncated by size
    all += "\n" + sub.markdown          # object_not_found here = permission gap, skip gracefully
```

Keep target pages under a few thousand blocks for best results.

## Creating a page from markdown

`POST /v1/pages` with `"parent": {"page_id": "..."}` plus a `markdown` string.

- `markdown` is **mutually exclusive** with `children` and `content`.
- Requires `insert_content` + `insert_property` capabilities.
- JSON must contain real `\n` escapes. With cURL wrap the body in single quotes; never use
  `$'...'` quoting (it converts `\n` into real newlines and produces invalid JSON).

```bash
curl -X POST https://api.notion.com/v1/pages \
  -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
  -H 'Content-Type: application/json' \
  -H 'Notion-Version: 2026-03-11' \
  --data '{"parent":{"page_id":"YOUR_PAGE_ID"},"markdown":"# Meeting Notes\nDiscussed priorities.\n- [ ] Draft proposal"}'
```

## Updating a page with markdown

`PATCH /v1/pages/{page_id}/markdown` is a discriminated union - pick exactly ONE `type`:

| Command | Status | Purpose |
| --- | --- | --- |
| `update_content` | preferred | targeted search-and-replace, up to 100 ops per call |
| `replace_content` | preferred | wipe and rewrite the entire page |
| `insert_content` | legacy | insert at start/end or after an ellipsis selection |
| `replace_content_range` | legacy | replace an ellipsis-selected range |

Prefer the two modern commands - more precise matching and better errors.

```json
{
  "type": "update_content",
  "update_content": {
    "content_updates": [
      { "old_str": "Draft proposal", "new_str": "Draft proposal (due Friday)" }
    ]
  }
}
```

```json
{
  "type": "replace_content",
  "replace_content": { "new_str": "# Fresh Start\nReplaces everything." }
}
```

Every variant returns the full updated page as `page_markdown`. Matching is case-sensitive.
Legacy selections use `"start text...end text"` ellipsis format; never combine
`insert_content.position` with `insert_content.after`.

## Large writes: go async

Big markdown bodies can exceed client timeouts. Set `"allow_async": true`
(top level of create/update request) to get HTTP 202 + an `async_task` handle:

```json
{ "object": "async_task", "id": "task_abc123", "status": "queued",
  "status_url": "https://api.notion.com/v1/async_tasks/task_abc123",
  "poll_after_seconds": 2 }
```

Poll the `status_url` until terminal status. Statuses: `queued`, `running`, `retrying`,
`succeeded`, `failed`. Use `poll_after_seconds` as the minimum delay. Validation can still fail
while running - always poll to the end. On `succeeded`, `result` holds the normal response;
on `failed`, `error` holds the standard API error. Task metadata expires after a bounded period,
so persist any final result you need. Also available in official Notion MCP via
`allow_async: true` on `create_pages` / `update_page` + `notion-get-async-task`.

## Block object anatomy

```json
{
  "object": "block",
  "id": "c02fc1d3-db8b-45c5-a222-27595b15aea7",
  "parent": { "type": "page_id", "page_id": "59833787-2cf9-4fdf-8782-e53db20768a5" },
  "type": "heading_2",
  "has_children": false,
  "in_trash": false,
  "heading_2": { "rich_text": [], "color": "green", "is_toggleable": false }
}
```

Key fields: `id` (UUIDv4), `parent`, `type` (enum), `created_time` / `last_edited_time`
(ISO 8601), `created_by` / `last_edited_by`, `in_trash` (replaces deprecated `archived`),
`has_children` (must fetch children separately when true), and one `{type}` payload object.
Unsupported Notion features surface as `"type": "unsupported"` with an informational
`unsupported.block_type` string (e.g. `form`, `button`, `drive`) - not an enum; new values appear
over time. Full per-type reference: `references/block-types.md`.

## Block-type constraints that bite

- **column_list**: needs ≥ 2 columns and each column ≥ 1 child at creation; columns can only be
  appended to column_lists; `width_ratio` values must sum to 1. Reading contents requires three
  nested get-children calls (page → column_list → column → content).
- **table**: `table_width` only at creation (updates fail); when appending, include at least one
  `table_row` whose `cells` length equals `table_width`.
- **child_page / child_database**: created via the page/database endpoints, never via append.
- **headings as toggles**: children allowed under headings only when `is_toggleable: true`.
- **synced_block**: create originals before duplicates (`synced_from: null` vs pointing at the
  original); content updates unsupported.
- **code**: language uses exact enum strings (`javascript`, `typescript`, `python`, `plain text`, ...).
- **audio (external)**: mp3, wav, ogg, oga, m4a only; more formats via File Upload API.
- **tab**: only paragraph blocks may be direct children; each paragraph child = one tab label/icon/content.
- **template**: deprecated - creation no longer supported since March 2023.

## Error handling quick table

| Code | Meaning / fix |
| --- | --- |
| `validation_error` | selection/old_str not found; multiple matches (use `replace_all_matches`); both position+after given; would delete child pages/databases without flag; wrong ID type; synced page target (`external_object_instance_page`); range spans transcript |
| `object_not_found` | page/block missing OR connection lacks access (treat as skip on unknown-block refetch) |
| `restricted_resource` | connection lacks the required capability (`read_content`, `update_content`, `insert_content`) |

Capability summary: read markdown → `read_content`; update markdown → `update_content`;
create page with markdown → `insert_content` (+ `insert_property`).

## Tool mapping across surfaces

| Operation | REST | notion-suekou MCP tools | Official Notion MCP |
| --- | --- | --- | --- |
| Read page as md | `GET /v1/pages/:id/markdown` | `retrieve_page_markdown(page_id, include_transcript)` | - |
| Update page md | `PATCH /v1/pages/:id/markdown` | `update_page_markdown(page_id, type, ...)` | `update_page` (command/new_str) |
| Create page w/ md | `POST /v1/pages` (markdown param) | `post_page` (children array) | `create_pages` (content) |
| Get block / children | `GET /v1/blocks/:id(+/children)` | `retrieve-a-block`, `get-block-children` | - |
| Append blocks | `PATCH /v1/blocks/:id/children` | `patch-block-children` | - |
| Update/delete block | `PATCH` / `DELETE /v1/blocks/:id` | `update-a-block`, `delete-a-block` | - |
| Poll async task | `GET /v1/async_tasks/:id` | - | `notion-get-async-task` |

When a high-level simplified tool exists, prefer it over raw JSON block payloads
(e.g. append simple markdown via the markdown-style tool before hand-building block objects).

## Known limitations in this workspace

- `notion_API-update-a-block` with a `table_row` payload fails validation on this MCP server.
  Working pattern (used by `toeic-save-to-notion`): append fresh rows via
  `notion_API-patch-block-children`, then delete stale empty rows via `notion_API-delete-a-block`.

## Verification checklist

Before finishing any Notion write task:

1. Re-read the page after writing and confirm structure matches intent.
2. Confirm `truncated: false` (or handled unknown blocks) so nothing was silently dropped.
3. Confirm no unintended deletions happened (check validation errors were resolved consciously).
4. For tables: header row intact, `cells` count == `table_width` on every row.
