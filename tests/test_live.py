"""Live tests — hit the real hurriyet.com.tr. Cautious: a few requests, then stop.

Run:  pytest tests/test_live.py -v
Skip: pytest -m "not live"  (or set HURRIYET_SKIP_LIVE=1)
"""
import os
import pathlib
import sys
import time
import unittest

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from hurriyet_mcp import http as _http
from hurriyet_mcp import news as _N

pytestmark = pytest.mark.live
SKIP = os.environ.get("HURRIYET_SKIP_LIVE") == "1"


@pytest.mark.skipif(SKIP, reason="HURRIYET_SKIP_LIVE=1")
class TestLive(unittest.TestCase):
    def test_gundem_is_real(self):
        rows = _N.parse_article_links(_http.fetch_section("gundem"))
        self.assertGreaterEqual(len(rows), 10)
        print(f"\nLIVE gundem: {len(rows)} headlines, first = {rows[0]['title'][:80]}")
        time.sleep(1)

    def test_article_is_real(self):
        rows = _N.parse_article_links(_http.fetch_section("gundem"))
        art = _N.parse_article_page(_http.fetch_article(rows[0]["url"]))
        self.assertTrue(art["headline"])
        self.assertTrue(art["date_published"])
        self.assertGreater(len(art["body"]), 100)
        print(f"\nLIVE article: {art['headline'][:80]} ({art['date_published']}, "
              f"{len(art['body'])} chars body)")
        time.sleep(1)

    def test_search_is_real(self):
        rows = _N.parse_article_links(_http.fetch_search("futbol"))
        self.assertGreaterEqual(len(rows), 5)
        print(f"\nLIVE search 'futbol' -> {_http.last_url}: {len(rows)} articles")
        time.sleep(1)

    def test_home_and_categories_are_real(self):
        home = _http.fetch_home()
        rows = _N.parse_article_links(home)
        cats = _N.list_categories(home)
        self.assertGreaterEqual(len(rows), 20)
        self.assertGreaterEqual(len(cats), 12)
        print(f"\nLIVE home: {len(rows)} links, {len(cats)} categories")
        time.sleep(1)

    def test_unknown_section_404s(self):
        with self.assertRaises(_http.HurriyetError):
            _http.fetch_section("boyle-bir-bolum-yok-xyz123")
