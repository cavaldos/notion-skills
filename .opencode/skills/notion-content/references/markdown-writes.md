# Notion Markdown Writes — Full Spec

Companion to `notion-content/SKILL.md`.
Source: https://developers.notion.com/guides/data-apis/working-with-markdown-content

All writes go through `PATCH /v1/pages/{page_id}/markdown` (or `POST /v1/pages` with a
`markdown` body param for creation). The request is a discriminated union: exactly one `type`
per request. Requires `update_content` capability (create requires `insert_content`
+ `insert_property`).

## Encoding rules

- Newlines in the markdown string must be REAL `\n` escapes in JSON.
  cURL: single-quote the `--data` body. Never `$'...'` quoting.
- `<br>` = line break INSIDE one paragraph block. `\n` = new block boundary.
- Matching (`old_str`, `after`, `content_range`) is case-sensitive.
- Transcript content is never matchable — spans crossing it fail with `validation_error`.

## Command 1 — update_content (preferred)

Targeted search-and-replace. Up to 100 operations per call, applied in order.

```json
{
  "type": "update_content",
  "update_content": {
    "allow_deleting_content": false,
    "content_updates": [
      { "old_str": "Draft proposal", "new_str": "Draft proposal (due Friday)" },
      { "old_str": "Schedule follow-up", "new_str": "Schedule follow-up with design",
        "replace_all_matches": true }
    ]
  }
}
```

Rules:
- Each `old_str` must match EXACTLY ONE location; multiple matches → `validation_error`
  unless `replace_all_matches: true` on that operation.
- No match → `validation_error`. Verify text by reading the page first.

Use for: fixing typos across docs, updating status lines, swapping one section's wording,
batch edits in one round-trip.

## Command 2 — replace_content (preferred)

Replace the ENTIRE page content.

```json
{
  "type": "replace_content",
  "replace_content": {
    "new_str": "# Fresh Start\nThis replaces all previous content.",
    "allow_deleting_content": true
  }
}
```

DANGER: without `allow_deleting_content: true`, any child pages/databases that would be
destroyed cause a `validation_error` listing them — that error is your safety net. Only set the
flag after reviewing that list. Never set it preemptively on pages containing subpages you did
not intend to delete.

## Command 3 — insert_content (legacy)

Insert at start / end / after an ellipsis selection. Do NOT combine `position` and `after`.

```json
{ "type": "insert_content", "insert_content":
  { "content": "## Latest update\nAdded at top.", "position": { "type": "start" } } }
```

```json
{ "type": "insert_content", "insert_content":
  { "content": "## New Section\nInserted.", "after": "# Meeting Notes...Action items" } }
```

Omit both → appends to end of page. `after` matches from first occurrence of start-text to
end-text ("start...end").

## Command 4 — replace_content_range (legacy)

```json
{ "type": "replace_content_range", "replace_content_range":
  { "content": "## Updated Section\nNew content.", "content_range": "## Old Section...end of old" } }
```

Same ellipsis selection format. Prefer update_content instead when possible.

## Response

Every variant returns the whole updated page:

```json
{ "object": "page_markdown", "id": "...", "markdown": "...full content...",
  "truncated": false, "unknown_block_ids": [] }
```

Verify your edit landed by checking this response — no extra read needed.

## Async mode

Add top-level `"allow_async": true` to create or update requests with large bodies.

- Initial response: HTTP 202 + async_task object
  `{object:"async_task", id:"task_abc123", status:"queued", status_url, poll_after_seconds}`.
- Poll GET status_url (or Retrieve an async task by id). Statuses:
  `queued` → `running` → (`retrying` →) `succeeded` | `failed`.
- Respect `poll_after_seconds` as minimum delay between polls.
- Validation can still FAIL during background execution — always poll to terminal state.
- `succeeded` → `result` contains the normal response shape.
- `failed` → `error` contains standard API error ({status, code, message}).
  Retryable infra failures show `retrying`; validation/permission failures need a corrected request.
- Task metadata is retained only for a bounded period — persist final results yourself.
- SDK: @notionhq/client v5.23.0+ supports allow_async on pages.create/updateMarkdown and
  notion.asyncTasks.retrieve().
- Official Notion MCP: pass allow_async to notion-create-pages / notion-update-page,
  poll with notion-get-async-task.

## Full error table

| Code | Trigger |
| --- | --- |
| validation_error | content_range/after matches nothing; old_str not found; old_str matches multiple locations without replace_all_matches; both insert position+after supplied; operation would delete child pages/databases without allow_deleting_content; provided ID is a database or non-page block; target is a synced page (external_object_instance_page); selection spans transcript text |
| object_not_found | page does not exist OR connection lacks access |
| restricted_resource | connection lacks update_content capability |

## Access control summary

| Endpoint | Public | Internal | Personal token | Capability |
| --- | --- | --- | --- | --- |
| Create (POST /v1/pages w/ markdown) | Yes | Yes | Yes | insert_content (+insert_property) |
| Read (GET .../markdown) | Yes | Yes | Yes | read_content |
| Update (PATCH .../markdown) | Yes | Yes | Yes | update_content |

## Recipe patterns

### Safe targeted edit flow
1. GET page markdown → confirm `truncated:false`, locate exact target text.
2. PATCH update_content with precise old_str (include enough surrounding context to be unique).
3. Check response markdown confirms the change.

### Full rewrite of an agent-generated page
1. Confirm the page has no child pages/databases you care about.
2. replace_content with new_str (no deletion flag needed if nothing would be deleted).
3. On validation_error listing children → decide: keep them (adjust content) or consciously set flag.

### Append-only journal/log pages
insert_content with position:{type:"start"} keeps newest-first ordering without touching history.

### Big migration (>timeout risk)
Same command + allow_async:true → poll to succeeded before declaring done.
