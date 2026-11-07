"""Domain logic: parse Hürriyet pages into compact dicts.

Data sources (all public, no login, no key):
- headlines: /<section>/ (gundem, ekonomi, dunya, sporarena, ...) —
  server-rendered article links, IDs in the URL slug
- article:  /<section>/<slug>-<id> — schema.org NewsArticle JSON-LD
  (headline, dates, section, word count) + articleBody
- search:   /arama/<keyword> — keyword page; known keywords redirect
  to a topic hub (/haberleri/<keyword>), parsed the same way
- latest:   / homepage — the day's article links
Stdlib parsing only (re / json / html).
"""
from __future__ import annotations

import html as _html
import json
import re

BASE = "https://www.hurriyet.com.tr"

# Curated news sections (slug -> Turkish display name). Verified present
# in the homepage nav on 2026-11-07.
SECTIONS = {
    "gundem": "Gündem",
    "ekonomi": "Ekonomi",
    "dunya": "Dünya",
    "sporarena": "Spor Arena",
    "kelebek-magazin": "Kelebek Magazin",
    "teknoloji": "Teknoloji",
    "egitim": "Eğitim",
    "seyahat": "Seyahat",
    "yasam": "Yaşam",
    "video": "Video",
    "astroloji": "Astroloji",
    "son-dakika-haberleri": "Son Dakika",
    "avrupa": "Avrupa",
    "hayat": "Hayat",
    "kitap-sanat": "Kitap & Sanat",
}

_ARTICLE_RE = re.compile(r"^/[^\"?]+-\d{6,}/?$")


def _clean(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", _html.unescape(str(text))).strip()


def _ld_json(html: str, want_type: str) -> dict | None:
    for m in re.finditer(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S
    ):
        try:
            data = json.loads(m.group(1))
        except (json.JSONDecodeError, ValueError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            types = t if isinstance(t, list) else [t]
            if want_type in types:
                return item
    return None


def parse_article_links(html: str) -> list[dict]:
    """Titled article links: href /<section>/<slug>-<id> with link text.

    Skips nav/footer chrome (short/empty titles) and dedupes by URL.
    Gallery links (/galeri-...) are kept and marked kind='gallery'.
    """
    out, seen = [], set()
    for href, inner in re.findall(
        r'href="(/[^"]+-\d{6,}/?)"[^>]*>(.*?)</a>', html, re.S
    ):
        if not _ARTICLE_RE.match(href):
            continue
        title = _clean(re.sub(r"<[^>]+>", "", inner))
        if len(title) < 15 or href in seen:
            continue
        seen.add(href)
        m = re.search(r"-(\d{6,})/?$", href)
        section = href.strip("/").split("/", 1)[0]
        out.append(
            {
                "title": title,
                "url": f"{BASE}{href}",
                "id": m.group(1) if m else "",
                "section": section,
                "kind": "gallery" if section.startswith("galeri") else "article",
            }
        )
    return out


def parse_article_page(html: str) -> dict:
    """Parse an article page via its NewsArticle JSON-LD + articleBody."""
    ld = _ld_json(html, "NewsArticle")
    if ld is None:
        raise ValueError("no NewsArticle structured data found on this page")
    body = _clean(ld.get("articleBody"))
    if not body:
        # Fallback: long <p> paragraphs, skipping script/nav junk.
        paras = []
        for p in re.findall(r"<p[^>]*>(.*?)</p>", html, re.S):
            t = _clean(re.sub(r"<[^>]+>", "", p))
            if len(t) > 120 and "addEventListener" not in t:
                paras.append(t)
        body = "\n\n".join(paras)
    image = ld.get("image")
    if isinstance(image, dict):
        image = image.get("url") or ""
    elif isinstance(image, list):
        image = image[0] if image else ""
    author = ld.get("author")
    if isinstance(author, dict):
        author = author.get("name") or ""
    elif isinstance(author, list) and author and isinstance(author[0], dict):
        author = author[0].get("name") or ""
    wc = ld.get("wordCount")
    try:
        wc = int(wc) if wc is not None else None
    except (TypeError, ValueError):
        pass
    return {
        "headline": _clean(ld.get("headline")),
        "section": _clean(ld.get("articleSection")),
        "date_published": ld.get("datePublished") or "",
        "date_modified": ld.get("dateModified") or "",
        "word_count": wc,
        "keywords": _clean(ld.get("keywords")),
        "author": _clean(author),
        "image": image or "",
        "body": body,
    }


def list_categories(html: str | None = None) -> list[dict]:
    """News sections. If homepage HTML is given, only sections actually
    linked from it are returned; otherwise the full curated list."""
    if html is None:
        wanted = set(SECTIONS)
    else:
        found = set(re.findall(r'href="(?:https://www\.hurriyet\.com\.tr)?/([^"/]+)/"', html))
        wanted = set(SECTIONS) & found
    return [
        {"slug": slug, "name": SECTIONS[slug], "url": f"{BASE}/{slug}/"}
        for slug in SECTIONS
        if slug in wanted
    ]
