"""Offline tests — parse real captured Hürriyet fixtures, no network."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from hurriyet_mcp import news as N

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"


class TestArticleLinks(unittest.TestCase):
    def test_gundem(self):
        rows = N.parse_article_links((FIX / "gundem.html").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 30)
        first = rows[0]
        self.assertEqual(first["id"], "43369434")
        self.assertEqual(first["section"], "gundem")
        self.assertEqual(first["kind"], "article")
        self.assertTrue(first["url"].startswith("https://www.hurriyet.com.tr/gundem/"))
        self.assertIn("Afyonkarahisar", first["title"])

    def test_search_page(self):
        rows = N.parse_article_links((FIX / "search.html").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 45)
        self.assertTrue(all(r["id"] for r in rows))

    def test_dedupe_and_short_titles(self):
        html = (
            '<a href="/gundem/x-y-12345678">Short</a>'
            '<a href="/gundem/uzun-baslik-haber-ornegi-12345678">Uzun başlıklı haber örneği burada</a>'
            '<a href="/gundem/uzun-baslik-haber-ornegi-12345678">Uzun başlıklı haber örneği burada</a>'
        )
        rows = N.parse_article_links(html)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "12345678")


class TestArticlePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = N.parse_article_page((FIX / "article.html").read_text(encoding="utf-8"))

    def test_meta(self):
        self.assertTrue(self.a["headline"].startswith("6 ilde Telegram"))
        self.assertEqual(self.a["section"], "Gündem")
        self.assertEqual(self.a["date_published"], "2026-11-07T09:38:51+03:00")
        self.assertEqual(self.a["word_count"], 143)

    def test_body(self):
        self.assertEqual(len(self.a["body"]), 931)
        self.assertTrue(self.a["body"].startswith("İzmir Cumhuriyet Başsavcılığı"))

    def test_no_newsarticle_raises(self):
        with self.assertRaises(ValueError):
            N.parse_article_page("<html><body>no ld here</body></html>")


class TestCategories(unittest.TestCase):
    def test_curated_list(self):
        cats = N.list_categories()
        self.assertEqual(len(cats), 15)
        slugs = [c["slug"] for c in cats]
        for want in ("gundem", "ekonomi", "dunya", "sporarena", "teknoloji"):
            self.assertIn(want, slugs)
        self.assertEqual(cats[0]["name"], "Gündem")


if __name__ == "__main__":
    unittest.main()
