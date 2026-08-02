#!/usr/bin/env python3
"""Download Notion databases to local JSON + Markdown files.

Usage:
    python3 .opencode/skills/toeic-essay/scripts/download_notion_db.py [--outdir notion-data]

Reads NOTION_TOKEN from env var, .env (root) or .opencode/.env.
Saves per database (project root is auto-detected, so this works from any CWD):
    <outdir>/<slug>/database.json   - database schema
    <outdir>/<slug>/pages.json      - all page results (raw)
    <outdir>/<slug>/data.md         - human-readable Markdown
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

# Project root = 5 levels up from this script (.opencode/skills/toeic-essay/scripts/)
PROJECT_ROOT = Path(__file__).resolve().parents[4]

API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"  # data sources API requires 2025-09-03+

# slug -> (name, data_source_id)  — data source ids from SKILL.md
DATABASES = {
    "popular_structure": (
        "Popular structure",
        "3acf312e-ab25-800e-992f-000bbf1f5cfe",
    ),
    "collocation": (
        "Collocation",
        "3aef312e-ab25-802b-b3e6-000b8d8c0152",
    ),
}


def load_token() -> str:
    """Read NOTION_TOKEN from env var, then .env or .opencode/.env."""
    env_token = os.environ.get("NOTION_TOKEN", "").strip()
    if env_token:
        return env_token
    for env_path in (PROJECT_ROOT / ".env", PROJECT_ROOT / ".opencode" / ".env"):
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("NOTION_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if token:
                        return token
    sys.exit("ERROR: NOTION_TOKEN not found (set env var or .env / .opencode/.env)")


def api_request(method: str, path: str, token: str, body: dict | None = None) -> dict:
    """Perform a Notion API request and return parsed JSON."""
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        sys.exit(f"ERROR: Notion API {e.code} for {path}\n{detail}")


def query_all_pages(ds_id: str, token: str) -> list[dict]:
    """Query a data source with pagination, returning all page results."""
    pages: list[dict] = []
    cursor: str | None = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        resp = api_request("POST", f"/data_sources/{ds_id}/query", token, body)
        pages.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return pages


def rich_text_value(value: dict) -> str:
    """Extract plain text from a rich_text property value."""
    return "".join(t.get("plain_text", "") for t in value or [])


def prop_value(prop: dict) -> str:
    """Flatten any property value into a plain string."""
    if prop is None:
        return ""
    ptype = prop.get("type")
    if ptype == "title":
        return rich_text_value(prop.get("title"))
    if ptype == "rich_text":
        return rich_text_value(prop.get("rich_text"))
    if ptype == "select":
        sel = prop.get("select")
        return sel.get("name", "") if sel else ""
    if ptype == "multi_select":
        return ", ".join(s.get("name", "") for s in prop.get("multi_select", []))
    if ptype == "url":
        return prop.get("url", "")
    if ptype == "number":
        return str(prop.get("number", ""))
    if ptype == "checkbox":
        return str(prop.get("checkbox", ""))
    if ptype == "date":
        d = prop.get("date")
        return d.get("start", "") if d else ""
    if ptype == "relation":
        return ", ".join(r.get("id", "") for r in prop.get("relation", []))
    return ""


def build_markdown(name: str, schema: dict, pages: list[dict]) -> str:
    """Render a readable Markdown table from the data source schema + pages.

    Note: the data sources API keys `properties` by property NAME (not id).
    """
    lines = [f"# {name}", ""]
    lines.append(f"Total pages: {len(pages)}")
    lines.append("")

    for page in pages:
        p = page.get("properties", {})
        # Title property first (the only title-type column)
        title_val = ""
        for pname, prop in p.items():
            if prop.get("type") == "title":
                title_val = rich_text_value(prop.get("title"))
                break
        lines.append(f"## {title_val or '(untitled)'}")
        lines.append("")
        lines.append("| Property | Value |")
        lines.append("| :--- | :--- |")
        for pname, prop in p.items():
            if prop.get("type") == "title":
                continue
            value = prop_value(prop)
            if value:
                # Escape pipes for table display
                value = value.replace("|", "\\|").replace("\n", "<br>")
                lines.append(f"| {pname} | {value} |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    outdir = PROJECT_ROOT / "notion-data"
    if len(sys.argv) > 1 and sys.argv[1] == "--outdir" and len(sys.argv) > 2:
        outdir = Path(sys.argv[2]).expanduser()
    if not outdir.is_absolute():
        outdir = PROJECT_ROOT / outdir

    token = load_token()
    outdir.mkdir(parents=True, exist_ok=True)

    for slug, (name, ds_id) in DATABASES.items():
        print(f"[1/2] Retrieving schema: {name} ...")
        schema = api_request("GET", f"/data_sources/{ds_id}", token)

        print(f"[2/2] Querying pages: {name} ...")
        pages = query_all_pages(ds_id, token)

        db_dir = outdir / slug
        db_dir.mkdir(parents=True, exist_ok=True)
        (db_dir / "database.json").write_text(
            json.dumps(schema, ensure_ascii=False, indent=2)
        )
        (db_dir / "pages.json").write_text(
            json.dumps(pages, ensure_ascii=False, indent=2)
        )
        (db_dir / "data.md").write_text(
            build_markdown(name, schema, pages), encoding="utf-8"
        )
        print(f"    -> {db_dir}/  ({len(pages)} pages)")
        print()

    print("Done. Data saved under", outdir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
