# hurriyet-mcp 🇹🇷

**Hürriyet** (hurriyet.com.tr) için gayriresmî, **salt-okunur** MCP sunucusu — Türkiye'nin haber sitesi: bölüm manşetleri, tam haber metni, anahtar kelime araması ve ana sayfanın son haberleri.

> "Türkiye MCP fabrikası" parçası (Sepehr tarzı pipeline). Hürriyet ile bağlantısı yoktur.

## Yapay zekâ ajanları için

MCP istemcinize ekleyin (stdio):

```json
{
  "mcpServers": {
    "hurriyet": {
      "command": "uvx",
      "args": ["hurriyet-mcp==0.1.1"]
    }
  }
}
```

## Araçlar

| Araç | Açıklama |
|------|----------|
| `hurriyet_get_headlines` | Bir bölümün son manşetleri — `section` (örn. `gundem`, `ekonomi`, `dunya`, `sporarena`), `limit` (1..30) |
| `hurriyet_get_article` | Tam haber metni — `url` (hurriyet.com.tr haber URL'si veya yolu) |
| `hurriyet_search_news` | Anahtar kelimeyle haber ara — `query`, `limit` (1..30) |
| `hurriyet_get_latest` | Ana sayfanın son haberleri, `limit` (1..30) |
| `hurriyet_list_categories` | Haber bölümleri (slug, Türkçe ad, url) |

Örnek (`hurriyet_get_headlines` / "gundem"): 30 manşet; ilk haber "Afyonkarahisar'da 8 kişiyi katletmişti! ..." Örnek (`hurriyet_get_article`): "6 ilde Telegram üzerinden asılsız ihbar ve şantaj yapan 7 şüpheli tutuklandı" — 7 Kasım 2026 09:38, 143 kelime.

Notlar:
- Haberler schema.org NewsArticle verisinden gelir (başlık, tarihler, bölüm, kelime sayısı, metin).
- Arama `/arama/<kelime>`; bilinen kelimeler konu sayfasına yönlenir (örn. `/haberleri/futbol`) — araç `landed_url`'yi bildirir.
- Veri: hurriyet.com.tr herkese açık sayfalar — giriş yok, API anahtarı yok, salt-okunur.

## Kurallar

Gayriresmî ve salt-okunur — giriş yok, API anahtarı yok, yazma yok. Testler: çevrimdışı fixture + canlı testler (12/12 yeşil).
