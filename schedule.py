"""Current-week LMU race schedule (Daily/Weekly/Special) from lmuschedule.com.

The site has no documented public API, but its frontend calls a backend at
api.lmuschedule.com that (as of writing) only checks the Referer header rather
than doing real origin/auth checks — likely an oversight, not an intentional
public API, so this could stop working at any time without notice. Every
failure mode here is handled by simply not showing the schedule section
rather than crashing, and a short cache keeps us from hammering their backend
on every button press.
"""
from __future__ import annotations

import logging
import time
from html import escape as html_escape

import aiohttp

from i18n import t

log = logging.getLogger(__name__)

_API_URL = "https://api.lmuschedule.com/racingschedules"
_HEADERS = {"Referer": "https://www.lmuschedule.com/", "Accept": "application/json"}
_CACHE_TTL = 600  # seconds

_cache: dict = {"data": None, "fetched_at": 0.0}

_DIFFICULTY_ORDER = ["Beginner", "Intermediate", "Advanced"]
_DIFFICULTY_EMOJI = {"Beginner": "🔰", "Intermediate": "🔶", "Advanced": "🔴"}


async def _fetch_raw() -> list[dict] | None:
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(_API_URL, headers=_HEADERS) as resp:
                if resp.status != 200:
                    log.warning("lmuschedule.com API returned HTTP %s", resp.status)
                    return None
                payload = await resp.json(content_type=None)
    except Exception:
        log.exception("Failed to fetch lmuschedule.com race schedule")
        return None
    body = payload.get("body") if isinstance(payload, dict) else payload
    if not isinstance(body, list):
        log.warning("Unexpected lmuschedule.com payload shape: %r", type(payload))
        return None
    return body


async def get_schedule(force: bool = False) -> list[dict] | None:
    """Cached current-week schedule. Returns None only if we have never
    successfully fetched it — a fresh fetch failure falls back to the last
    known-good data so a transient hiccup on their end doesn't blank the bot."""
    now = time.time()
    if not force and _cache["data"] is not None and now - _cache["fetched_at"] < _CACHE_TTL:
        return _cache["data"]
    fresh = await _fetch_raw()
    if fresh is not None:
        _cache["data"] = fresh
        _cache["fetched_at"] = now
    return _cache["data"]


def format_schedule(body: list[dict], lang: str) -> str:
    daily = [r for r in body if r.get("raceType") == "Daily Races"]
    weekly = [r for r in body if r.get("raceType") == "Weekly Races"]
    special = [r for r in body if r.get("raceType") == "Special Event"]

    lines = [t(lang, "schedule_header"), ""]

    for diff in _DIFFICULTY_ORDER:
        entries = sorted(
            (r for r in daily if r.get("difficulty") == diff),
            key=lambda r: r.get("circuit", ""),
        )
        if not entries:
            continue
        lines.append(f"{_DIFFICULTY_EMOJI.get(diff, '')} <b>{t(lang, f'difficulty_{diff.lower()}')}</b>")
        for r in entries:
            series = html_escape(str(r.get("series") or "?"))
            circuit = html_escape(str(r.get("circuit") or "?"))
            lines.append(f"  🏁 {series} — {circuit}")
        lines.append("")

    def _block(entries: list[dict], header_key: str) -> None:
        if not entries:
            return
        lines.append(f"<b>{t(lang, header_key)}</b>")
        for r in entries:
            series = html_escape(str(r.get("series") or "?"))
            circuit = html_escape(str(r.get("circuit") or "?"))
            classes = html_escape(", ".join(r.get("carClasses") or []))
            lines.append(f"  {series} — {circuit}")
            if classes:
                lines.append(f"  {t(lang, 'schedule_classes')}: {classes}")
        lines.append("")

    _block(weekly, "schedule_weekly")
    _block(special, "schedule_special")

    lines.append(t(lang, "schedule_footer"))
    return "\n".join(lines).strip()
