/**
 * tool-tracker — OpenCode TUI sidebar plugin.
 *
 * Shows in the right sidebar:
 *  - every tool call of the active session (live status icons)
 *  - an aggregated "Skills" section counting native `skill` tool invocations
 *
 * Registered from .opencode/tui.json:
 *   { "plugin": ["./plugins/tool-tracker.tsx"] }
 *
 * Data source: api.state.session.messages() — the same synced TUI state
 * the built-in sidebar sections (context / mcp / todo / files) render from.
 */

/** @jsxImportSource @opentui/solid */

import type {
  TuiPlugin,
  TuiPluginApi,
  TuiPluginModule,
  TuiSlotPlugin,
} from "@opencode-ai/plugin/tui"

const ID = "tool-tracker"
/** Render above built-in sections: context 100, mcp 200, lsp 300, todo 400, files 500. */
const ORDER = 60
const MAX_TOOLS = 14
const TITLE_MAX = 34

type RecordOf<T extends object> = { [K in keyof T]: unknown }
type UnknownRecord = Record<string, unknown>

const isRecord = (value: unknown): value is UnknownRecord =>
  typeof value === "object" && value !== null && !Array.isArray(value)

const asString = (value: unknown): string | undefined =>
  typeof value === "string" ? value : undefined

const clampText = (value: unknown, max: number): string => {
  const text = (asString(value) ?? "").replace(/\s+/g, " ").trim()
  if (!text) return ""
  return text.length > max ? `${text.slice(0, max - 1)}…` : text
}

type ToolStatus = "pending" | "running" | "completed" | "error"

type ToolRow = {
  key: string
  tool: string
  status: ToolStatus
  title: string
}

const normalizeStatus = (value: unknown): ToolStatus => {
  switch (asString(value)) {
    case "running":
      return "running"
    case "completed":
      return "completed"
    case "error":
      return "error"
    default:
      return "pending"
  }
}

/** Extract tool-call rows from session messages, tolerating either
 *  `{ info, parts }` envelopes or flat message records. */
const extractToolRows = (input: unknown): ToolRow[] => {
  if (!Array.isArray(input)) return []
  const rows: ToolRow[] = []

  for (const entry of input) {
    if (!isRecord(entry)) continue
    const info = isRecord(entry.info) ? entry.info : entry
    const parts = entry.parts ?? info.parts
    if (!Array.isArray(parts)) continue
    const messageId = asString(info.id) ?? String(rows.length)

    for (const raw of parts) {
      if (!isRecord(raw) || raw.type !== "tool") continue
      const state = isRecord(raw.state) ? raw.state : {}
      rows.push({
        key: asString(raw.id) ?? `${messageId}:${asString(raw.callID) ?? rows.length}`,
        tool: asString(raw.tool) ?? "unknown",
        status: normalizeStatus(state.status),
        title: clampText(state.title, TITLE_MAX),
      })
    }
  }

  return rows.slice(-MAX_TOOLS)
}

const readToolRows = (api: TuiPluginApi, sessionId: string): ToolRow[] => {
  try {
    const state = api.state as unknown as RecordOf<{ session: RecordOf<{ messages: (id: string) => unknown }> }>
    const session = isRecord(state.session) ? state.session : undefined
    const messages = session?.messages
    if (typeof messages !== "function") return []
    return extractToolRows(messages.call(session, sessionId))
  } catch {
    return []
  }
}

type SkillRow = {
  key: string
  name: string
  status: ToolStatus
  count: number
}

/** Pull the invoked skill name out of a `skill` tool part's state. */
const skillNameOf = (state: UnknownRecord): string => {
  const input = isRecord(state.input) ? state.input : undefined
  const named = asString(input?.name)
  if (named) return clampText(named, TITLE_MAX)
  // Fallback: parse titles like "skill(notion-content)".
  const match = /\(([^)]+)\)/.exec(asString(state.title) ?? "")
  return match ? clampText(match[1], TITLE_MAX) : ""
}

/** Aggregate native `skill` tool calls of the session into counted rows,
 *  ordered by most recent use. Tolerates `{ info, parts }` envelopes
 *  or flat message records, same as extractToolRows. */
const extractSkillRows = (input: unknown): SkillRow[] => {
  if (!Array.isArray(input)) return []
  const calls: { name: string; status: ToolStatus }[] = []

  for (const entry of input) {
    if (!isRecord(entry)) continue
    const info = isRecord(entry.info) ? entry.info : entry
    const parts = entry.parts ?? info.parts
    if (!Array.isArray(parts)) continue

    for (const raw of parts) {
      if (!isRecord(raw) || raw.type !== "tool") continue
      if ((asString(raw.tool) ?? "") !== "skill") continue
      const state = isRecord(raw.state) ? raw.state : {}
      const name = skillNameOf(state)
      if (!name || name === "unknown") continue
      calls.push({ name, status: normalizeStatus(state.status) })
    }
  }

  const byName = new Map<string, SkillRow>()
  for (const call of [...calls].reverse()) {
    const existing = byName.get(call.name)
    byName.set(call.name, {
      key: call.name,
      name: call.name,
      status:
        existing === undefined
          ? call.status
          : existing.status === "error"
            ? "error"
            : call.status,
      count: (existing?.count ?? 0) + 1,
    })
  }
  return [...byName.values()]
}

const readSkillRows = (api: TuiPluginApi, sessionId: string): SkillRow[] => {
  try {
    const state = api.state as unknown as RecordOf<{ session: RecordOf<{ messages: (id: string) => unknown }> }>
    const session = isRecord(state.session) ? state.session : undefined
    const messages = session?.messages
    if (typeof messages !== "function") return []
    return extractSkillRows(messages.call(session, sessionId))
  } catch {
    return []
  }
}



type Skin = {
  accent: string
  border: string
  error: string
  muted: string
  panel: string
  success: string
  text: string
  warning: string
}

const ink = (tokens: UnknownRecord, name: string, fallback: string): string => {
  const value = tokens[name]
  return typeof value === "string" ? value : fallback
}

const look = (theme: unknown): Skin => {
  const tokens = isRecord(theme) ? theme : {}
  return {
    panel: ink(tokens, "backgroundPanel", "#1d1d1d"),
    border: ink(tokens, "border", "#4a4a4a"),
    text: ink(tokens, "text", "#f0f0f0"),
    muted: ink(tokens, "textMuted", "#a5a5a5"),
    accent: ink(tokens, "primary", "#5f87ff"),
    success: ink(tokens, "success", "#4ec9b0"),
    warning: ink(tokens, "warning", "#d7ba7d"),
    error: ink(tokens, "error", "#f14c4c"),
  }
}

const STATUS_ICON: Record<ToolStatus, string> = {
  pending: "○",
  running: "◐",
  completed: "✔",
  error: "✘",
}

const statusColor = (status: ToolStatus, skin: Skin): string => {
  switch (status) {
    case "completed":
      return skin.success
    case "error":
      return skin.error
    case "running":
      return skin.warning
    default:
      return skin.muted
  }
}

const createTracker = (api: TuiPluginApi): TuiSlotPlugin => ({
  order: ORDER,
  slots: {
    sidebar_content(ctx, value) {
      const skin = look(ctx.theme.current)
      // Read inside JSX expressions so updates stay reactive with the host store.
      const sessionId = asString(
        (isRecord(value) ? (value as UnknownRecord).session_id : undefined),
      )

      if (!sessionId) {
        return (
          <box flexDirection="column">
            <text fg={skin.accent}>
              <b>Tools</b>
            </text>
            <text fg={skin.muted}>no active session</text>
          </box>
        )
      }

      return (
        <box flexDirection="column">
          <text fg={skin.accent}>
            <b>Tools</b>
          </text>
          {(() => {
            const rows = readToolRows(api, sessionId)
            if (rows.length === 0) {
              return (
                <text fg={skin.muted}>no tool calls yet</text>
              )
            }
            return rows.map((row) => (
              <text>
                <span style={{ fg: statusColor(row.status, skin) }}>{STATUS_ICON[row.status]} </span>
                <span style={{ fg: skin.text }}>{row.tool}</span>
                {row.title ? <span style={{ fg: skin.muted }}> {row.title}</span> : null}
              </text>
            ))
          })()}
          {(() => {
            const skills = readSkillRows(api, sessionId)
            if (skills.length === 0) return null
            return (
              <box flexDirection="column">
                <text fg={skin.accent}>
                  <b>Skills</b>
                </text>
                {skills.map((skill) => (
                  <text>
                    <span style={{ fg: statusColor(skill.status, skin) }}>{STATUS_ICON[skill.status]} </span>
                    <span style={{ fg: skin.text }}>{skill.name}</span>
                    {skill.count > 1 ? <span style={{ fg: skin.muted }}> ×{skill.count}</span> : null}
                  </text>
                ))}
              </box>
            )
          })()}
        </box>
      )
    },
  },
})

const tui: TuiPlugin = async (api) => {
  api.slots.register(createTracker(api))
}

const plugin: TuiPluginModule & { id: string } = {
  id: ID,
  tui,
}

export default plugin
