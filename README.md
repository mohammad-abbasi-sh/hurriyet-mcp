# hurriyet-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/hurriyet-mcp

Unofficial **read-only** MCP server for **Hürriyet** (hurriyet.com.tr) — Türkiye's news: section headlines, full article text, keyword search and the homepage's latest news.

> Part of the "Turkey MCP factory" (Sepehr-style pipeline). Not affiliated with Hürriyet.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "hurriyet": {
      "command": "uvx",
      "args": ["hurriyet-mcp"]
    }
  }
}
```

Or run locally: `python -m hurriyet_mcp.server` (needs `mcp<2`, `curl-cffi`, `requests`).

## Tools

| Tool | Description |
|------|-------------|
| `hurriyet_get_headlines` | Latest headlines from a section — `section` (e.g. `gundem`, `ekonomi`, `dunya`, `sporarena`), `limit` (1..30) |
| `hurriyet_get_article` | Full article text — `url` (hurriyet.com.tr article URL or path) |
| `hurriyet_search_news` | Search news by keyword — `query`, `limit` (1..30) |
| `hurriyet_get_latest` | Latest news from the homepage, `limit` (1..30) |
| `hurriyet_list_categories` | News sections (slug, Turkish name, url) |

Example output (`hurriyet_get_headlines` / "gundem"):

```json
{"section": "gundem", "count": 10,
 "articles": [{"title": "Afyonkarahisar'da 8 kişiyi katletmişti! ...",
   "url": "https://www.hurriyet.com.tr/gundem/...-43369434",
   "id": "43369434", "section": "gundem", "kind": "article"}]}
```

Example output (`hurriyet_get_article`):

```json
{"headline": "6 ilde Telegram üzerinden asılsız ihbar ve şantaj yapan 7 şüpheli tutuklandı",
 "section": "Gündem", "date_published": "2026-11-07T09:38:51+03:00",
 "word_count": 143, "body": "İzmir Cumhuriyet Başsavcılığı koordinesinde ..."}
```

Notes:
- Articles come from schema.org NewsArticle data (headline, dates, section, word count, body).
- Search is `/arama/<keyword>`; known keywords redirect to a topic hub (e.g. `/haberleri/futbol`) — the tool reports the `landed_url`.
- The `/arama/` path is slow under TLS impersonation — the server falls back to plain requests there.
- Data: hurriyet.com.tr public pages — no key, no login, read-only.

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" curl-cffi requests pytest
.venv/bin/python -m pytest tests/ -q
```

- `tests/test_news.py` — offline, parses real captured fixtures
- `tests/test_live.py` — 5 cautious live requests against hurriyet.com.tr

## License

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
