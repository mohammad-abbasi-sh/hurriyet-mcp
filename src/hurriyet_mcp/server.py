"""MCP server: unofficial read-only access to Hürriyet news."""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from . import http as _http
from . import news as _N

mcp = FastMCP("hurriyet-mcp")

INSTRUCTIONS = """\
Unofficial read-only MCP server for Hürriyet (hurriyet.com.tr), \
Türkiye's news site — section headlines, full articles, keyword \
search and the homepage's latest news. Articles come from the \
site's server-rendered pages with schema.org NewsArticle data \
(headline, dates, section, word count, body). Search is \
/arama/<keyword>; known keywords redirect to a topic hub \
(e.g. /haberleri/futbol) and the tool reports the final URL it \
landed on. No login, no API key. Read-only; transport uses Chrome \
TLS impersonation with a plain-requests fallback (the /arama/ path \
is slow under impersonation); requests are spaced ~1s apart. Built \
by Mohammad Abbasi (mohammad-abbasi-sh) — Turkey MCP factory.\
"""


def _err(e: Exception) -> str:
    return json.dumps({"error": str(e)}, ensure_ascii=False)


def _validate_limit(limit: int, lo: int = 1, hi: int = 30) -> int:
    if not lo <= limit <= hi:
        raise ValueError(f"limit must be between {lo} and {hi}")
    return limit


@mcp.tool()
def hurriyet_get_headlines(section: str = "gundem", limit: int = 10) -> str:
    """Latest headlines from a Hürriyet section.
    section: e.g. "gundem", "ekonomi", "dunya", "sporarena",
    "kelebek-magazin", "teknoloji" (see hurriyet_list_categories).
    limit 1..30."""
    try:
        s = section.strip().strip("/").lower()
        if s not in _N.SECTIONS:
            raise ValueError(
                f"unknown section {section!r}; known: {', '.join(_N.SECTIONS)}"
            )
        _validate_limit(limit)
        rows = _N.parse_article_links(_http.fetch_section(s))
    except (ValueError, _http.HurriyetError) as e:
        return _err(e)
    return json.dumps(
        {"section": s, "count": len(rows[:limit]), "articles": rows[:limit]},
        ensure_ascii=False,
    )


@mcp.tool()
def hurriyet_get_article(url: str) -> str:
    """Full article text. url: a hurriyet.com.tr article URL
    (or its path, e.g. /gundem/<slug>-<id>)."""
    try:
        if not url or not url.strip():
            raise ValueError("url must not be empty")
        art = _N.parse_article_page(_http.fetch_article(url.strip()))
    except (ValueError, _http.HurriyetError) as e:
        return _err(e)
    return json.dumps({"url": url.strip(), **art}, ensure_ascii=False)


@mcp.tool()
def hurriyet_search_news(query: str, limit: int = 10) -> str:
    """Search Hürriyet news by keyword.
    query: e.g. "deprem", "futbol", "ekonomi". limit 1..30.
    Known keywords redirect to a topic hub — the returned
    `landed_url` shows where the search actually landed."""
    try:
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        _validate_limit(limit)
        rows = _N.parse_article_links(_http.fetch_search(query.strip()))
        landed = _http.last_url
    except (ValueError, _http.HurriyetError) as e:
        return _err(e)
    return json.dumps(
        {
            "query": query.strip(),
            "landed_url": landed,
            "count": len(rows[:limit]),
            "articles": rows[:limit],
        },
        ensure_ascii=False,
    )


@mcp.tool()
def hurriyet_get_latest(limit: int = 10) -> str:
    """Latest news from the Hürriyet homepage. limit 1..30."""
    try:
        _validate_limit(limit)
        rows = _N.parse_article_links(_http.fetch_home())
    except (ValueError, _http.HurriyetError) as e:
        return _err(e)
    return json.dumps(
        {"count": len(rows[:limit]), "articles": rows[:limit]}, ensure_ascii=False
    )


@mcp.tool()
def hurriyet_list_categories() -> str:
    """Hürriyet news sections (slug, Turkish name, url)."""
    try:
        cats = _N.list_categories(_http.fetch_home())
    except (ValueError, _http.HurriyetError) as e:
        return _err(e)
    return json.dumps({"count": len(cats), "categories": cats}, ensure_ascii=False)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    import sys

    sys.exit(main())
