# hurriyet-mcp 🇹🇷

سرور MCP غیررسمی و **فقط‌خواندنی** برای **Hürriyet** (hurriyet.com.tr) — سایت خبری ترکیه: تیترهای بخش‌ها، متن کامل خبر، جست‌وجوی خبری و آخرین خبرهای صفحه‌ی اصلی.

> بخشی از «کارخانه‌ی MCP ترکیه» (پایپ‌لاین به سبک سپهر). هیچ وابستگی به Hürriyet ندارد.

## برای ایجنت‌های هوش مصنوعی

```json
{
  "mcpServers": {
    "hurriyet": {
      "command": "uvx",
      "args": ["hurriyet-mcp==0.1.0"]
    }
  }
}
```

## ابزارها

| ابزار | توضیح |
|------|-------|
| `hurriyet_get_headlines` | آخرین تیترهای یک بخش — `section` (مثلاً `gundem`، ‏`ekonomi`، ‏`dunya`، ‏`sporarena`)، ‏`limit` (۱ تا ۳۰) |
| `hurriyet_get_article` | متن کامل خبر — `url` (URL خبر hurriyet.com.tr یا مسیر آن) |
| `hurriyet_search_news` | جست‌وجوی اخبار با کلیدواژه — `query`، ‏`limit` (۱ تا ۳۰) |
| `hurriyet_get_latest` | آخرین خبرهای صفحه‌ی اصلی، `limit` (۱ تا ۳۰) |
| `hurriyet_list_categories` | بخش‌های خبری (slug، نام ترکی، url) |

مثال (`hurriyet_get_headlines` / «gundem»): ۳۰ تیتر؛ اولین خبر «Afyonkarahisar'da 8 kişiyi katletmişti! ...». مثال (`hurriyet_get_article`): «6 ilde Telegram üzerinden asılsız ihbar ve şantaj yapan 7 şüpheli tutuklandı» — ۷ نوامبر ۲۰۲۶، ۱۴۳ کلمه.

نکته‌ها:
- خبرها از داده‌ی schema.org NewsArticle می‌آیند (تیتر، تاریخ‌ها، بخش، تعداد کلمات، متن).
- جست‌وجو `/arama/<کلیدواژه>` است؛ کلیدواژه‌های شناخته‌شده به صفحه‌ی موضوعی هدایت می‌شوند (مثلاً `/haberleri/futbol`) — ابزار `landed_url` را گزارش می‌کند.
- داده: صفحات عمومی hurriyet.com.tr — بدون لاگین، بدون کلید، فقط‌خواندنی.

## قوانین

غیررسمی و فقط‌خواندنی — بدون لاگین، بدون کلید، بدون نوشتن. تست‌ها: آفلاین با فیکسچر + تست زنده (۱۲/۱۲ سبز).
