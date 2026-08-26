#!/usr/bin/env python3
"""Search locally downloaded Notion data (from download_notion_db.py).

Usage:
    python3 .opencode/skills/toeic-essay/scripts/search_notion_db.py KEYWORD [KEYWORD2 ...] [options]

Options:
    --db <slug>          Only search one database: popular_structure | collocation
    --type <name>        Filter by Type (popular_structure only, e.g. "Opinion")
    --topic <name>       Filter by Topic (collocation only, e.g. "Work & Career")
    --list-types         List all Type values in popular_structure and exit
    --list-topics        List all Topic values in collocation and exit
    --limit N            Max results shown per database (default 20)
    --data-dir <path>    Data folder (default notion-data at project root)

Examples:
    python3 .opencode/skills/toeic-essay/scripts/search_notion_db.py productivity
    python3 .opencode/skills/toeic-essay/scripts/search_notion_db.py "in my view" --db popular_structure --type Opinion
    python3 .opencode/skills/toeic-essay/scripts/search_notion_db.py turnover --db collocation --topic "Work & Career"
    python3 .opencode/skills/toeic-essay/scripts/search_notion_db.py --list-topics
"""

import argparse
import json
import sys
from pathlib import Path

# Project root = 5 levels up from this script (.opencode/skills/toeic-essay/scripts/)
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / "notion-data"
DATABASE_NAMES = {
    "popular_structure": "Popular structure",
    "collocation": "Collocation",
}


def load_pages(db_slug: str) -> list[dict]:
    path = DATA_DIR / db_slug / "pages.json"
    if not path.exists():
        sys.exit(f"ERROR: {path} not found. Run download_notion_db.py first.")
    return json.loads(path.read_text())


def page_texts(props: dict) -> dict[str, str]:
    """Flatten a page's properties into {property_name: plain_text}."""
    out: dict[str, str] = {}
    for pname, prop in props.items():
        ptype = prop.get("type")
        if ptype == "title":
            out[pname] = "".join(t.get("plain_text", "") for t in prop.get("title") or [])
        elif ptype == "rich_text":
            out[pname] = "".join(t.get("plain_text", "") for t in prop.get("rich_text") or [])
        elif ptype == "select":
            sel = prop.get("select")
            out[pname] = sel.get("name", "") if sel else ""
        elif ptype == "multi_select":
            out[pname] = ", ".join(s.get("name", "") for s in prop.get("multi_select", []))
    return out


def search_db(db_slug: str, keywords: list[str], filter_col: str | None,
              filter_val: str | None, limit: int) -> None:
    pages = load_pages(db_slug)
    kw_lower = [k.lower() for k in keywords]

    results: list[tuple[int, str, dict[str, str]]] = []
    for page in pages:
        texts = page_texts(page.get("properties", {}))
        # Apply Type/Topic filter if given
        if filter_col and filter_val:
            if texts.get(filter_col, "").lower() != filter_val.lower():
                continue
        haystack = " ".join(texts.values()).lower()
        if not all(k in haystack for k in kw_lower):
            continue
        # Score: keyword in title weighs more than in other fields
        title = next((v for k, v in texts.items()
                      if k.lower() in ("name", "collocation", "title")), "")
        score = sum(3 if k in title.lower() else 1 for k in kw_lower)
        results.append((score, title, texts))

    if not results:
        print(f"[{DATABASE_NAMES[db_slug]}] No matches.")
        return

    results.sort(key=lambda r: -r[0])
    print(f"[{DATABASE_NAMES[db_slug]}] {len(results)} match(es)"
          + (f" (showing first {limit})" if len(results) > limit else "") + ":")
    print()
    for score, title, texts in results[:limit]:
        print(f"### {title or '(untitled)'}")
        for pname, value in texts.items():
            if value and pname.lower() not in ("name", "collocation", "title"):
                print(f"  {pname}: {value}")
        print()


def list_values(db_slug: str, column: str) -> None:
    pages = load_pages(db_slug)
    values: set[str] = set()
    for page in pages:
        texts = page_texts(page.get("properties", {}))
        if texts.get(column):
            values.add(texts[column])
    print(f"[{DATABASE_NAMES[db_slug]}] {column} values ({len(values)}):")
    for v in sorted(values):
        print(f"  - {v}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("keywords", nargs="*", help="Search keywords (case-insensitive)")
    parser.add_argument("--db", choices=sorted(DATABASE_NAMES), help="Only search one database")
    parser.add_argument("--type", dest="type_filter", help="Filter by Type (popular_structure)")
    parser.add_argument("--topic", help="Filter by Topic (collocation)")
    parser.add_argument("--list-types", action="store_true", help="List Type values and exit")
    parser.add_argument("--list-topics", action="store_true", help="List Topic values and exit")
    parser.add_argument("--limit", type=int, default=20, help="Max results per database")
    parser.add_argument("--data-dir", default=None, help="Data folder (default notion-data at project root)")
    args = parser.parse_args()

    global DATA_DIR
    if args.data_dir:
        data_dir = Path(args.data_dir).expanduser()
        DATA_DIR = data_dir if data_dir.is_absolute() else PROJECT_ROOT / data_dir

    if args.list_types:
        list_values("popular_structure", "Type")
        return 0
    if args.list_topics:
        list_values("collocation", "Topic")
        return 0
    if not args.keywords:
        parser.error("At least one KEYWORD is required (or use --list-types / --list-topics)")

    # Sanity: filters must match the right database
    if args.type_filter and args.db == "collocation":
        sys.exit("ERROR: --type is for popular_structure; use --topic for collocation.")
    if args.topic and args.db == "popular_structure":
        sys.exit("ERROR: --topic is for collocation; use --type for popular_structure.")

    db_slugs = [args.db] if args.db else list(DATABASE_NAMES)
    for slug in db_slugs:
        filter_col, filter_val = None, None
        if args.type_filter and slug == "popular_structure":
            filter_col, filter_val = "Type", args.type_filter
        if args.topic and slug == "collocation":
            filter_col, filter_val = "Topic", args.topic
        search_db(slug, args.keywords, filter_col, filter_val, args.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
