"""HTTP layer for hurriyet_mcp.

hurriyet.com.tr serves its pages server-rendered with no login and
no API key. Search is a plain path (``/arama/<keyword>``) — known
keywords redirect to a topic hub (e.g. /haberleri/futbol), which the
parser handles the same way. Transport uses curl-cffi chrome120
impersonation (the proven Turkey-factory pattern) with a
plain-requests fallback: the /arama/ path timed out twice under
curl-cffi while plain requests answered in ~3s, so the fallback is
load-bearing here, not decorative. Requests are kept gentle (one at
a time, ~1s apart) and read-only.
"""
from __future__ import annotations

import time
from urllib.parse import quote

from curl_cffi import requests as _creq
import requests as _plain

BASE = "https://www.hurriyet.com.tr"
TIMEOUT = 60.0
MIN_INTERVAL = 1.0  # seconds between requests — be polite

_HEADERS = {
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_last_fetch = 0.0
last_url: str = ""


class HurriyetError(RuntimeError):
    pass


def _throttle() -> None:
    global _last_fetch
    wait = MIN_INTERVAL - (time.monotonic() - _last_fetch)
    if wait > 0:
        time.sleep(wait)
    _last_fetch = time.monotonic()


_PROFILES = ("chrome120", "chrome131", "safari17_0")
_MAX_ATTEMPTS = 2  # one retry with the next profile
_RETRY_BACKOFF = 1.0  # seconds between attempts
_profile_idx = 0  # sticky: profile that last succeeded


def _request(url: str, headers: dict, timeout: float = TIMEOUT):
    """GET with fingerprint rotation.

    Starts at the sticky profile (chrome120 on a fresh process), retries
    once with the next profile on HTTP 403/429 or a transport error, then
    returns the last response (so the caller raises the specific 403/429
    error) or raises a network error if every attempt failed at the
    transport. Added 2026-11-10 (fleet audit fix).
    """
    global _profile_idx
    last_exc: Exception | None = None
    for k in range(_MAX_ATTEMPTS):
        profile = _PROFILES[(_profile_idx + k) % len(_PROFILES)]
        try:
            resp = _creq.get(url, impersonate=profile, headers=headers, timeout=timeout)
        except Exception as e:
            last_exc = e
            if k + 1 < _MAX_ATTEMPTS:
                time.sleep(_RETRY_BACKOFF)
                continue
            raise HurriyetError(f"network error fetching {url}: {e}") from e
        if resp.status_code in (403, 429):
            if k + 1 < _MAX_ATTEMPTS:
                time.sleep(_RETRY_BACKOFF)
                continue
            return resp
        _profile_idx = (_profile_idx + k) % len(_PROFILES)
        return resp
    raise HurriyetError(f"network error fetching {url}: {last_exc}") from last_exc


def _get(url: str) -> str:
    global last_url
    _throttle()
    try:
        resp = _request(url, _HEADERS)
        status, text, final = resp.status_code, resp.text, str(resp.url)
    except Exception:
        # Fallback transport: plain requests with a browser UA.
        try:
            resp = _plain.get(
                url, headers={**_HEADERS, "User-Agent": _UA}, timeout=TIMEOUT
            )
            status, text, final = resp.status_code, resp.text, resp.url
        except HurriyetError:
            raise
        except Exception as e:
            raise HurriyetError(f"network error fetching {url}: {e}") from e
    last_url = final
    if status == 403:
        raise HurriyetError(
            "hurriyet.com.tr refused the request (HTTP 403, bot wall) — try again later"
        )
    if status == 429:
        raise HurriyetError(
            "hurriyet.com.tr rate-limited the request (HTTP 429) — try again later"
        )
    if status == 404:
        raise HurriyetError(f"hurriyet.com.tr has no page at {url} (HTTP 404)")
    if status != 200:
        raise HurriyetError(f"hurriyet.com.tr returned HTTP {status} for {url}")
    return text


def fetch_home() -> str:
    return _get(f"{BASE}/")


def fetch_section(section: str) -> str:
    return _get(f"{BASE}/{section.strip('/')}/")


def fetch_search(query: str) -> str:
    return _get(f"{BASE}/arama/{quote(query)}")


def fetch_article(path: str) -> str:
    path = path.strip()
    if path.startswith("http"):
        return _get(path)
    return _get(f"{BASE}/{path.lstrip('/')}")


def health_check() -> dict:
    """One polite probe of the source site.

    Returns {"status": "ok"|"blocked"|"error", "http_status": int|None,
    "url": ..., "detail": ...}. Used by the `hurriyet_health` tool
    and the daily smoke CI. Added 2026-11-10 (fleet audit fix).
    """
    url = "https://www.hurriyet.com.tr/"
    try:
        fetch_home()
    except HurriyetError as e:
        msg = str(e)
        if "403" in msg:
            return {"status": "blocked", "http_status": 403, "url": url, "detail": msg}
        if "429" in msg:
            return {"status": "blocked", "http_status": 429, "url": url, "detail": msg}
        return {"status": "error", "http_status": None, "url": url, "detail": msg}
    return {"status": "ok", "http_status": 200, "url": url}
