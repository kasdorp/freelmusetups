"""Tiny JSON persistence: per-user language + download counters."""
from __future__ import annotations

import json
import threading
from typing import Any

from config import ADMIN_IDS, DATA_DIR

_lock = threading.Lock()
_USERS_FILE = DATA_DIR / "users.json"
_STATS_FILE = DATA_DIR / "stats.json"
_SETTINGS_FILE = DATA_DIR / "settings.json"
_ADMINS_FILE = DATA_DIR / "admins.json"


def _load(path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save(path, data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    tmp.replace(path)


_users: dict[str, Any] = _load(_USERS_FILE)
_stats: dict[str, Any] = _load(_STATS_FILE)
_settings: dict[str, Any] = _load(_SETTINGS_FILE)
_admins: dict[str, Any] = _load(_ADMINS_FILE)

if "downloads" in _stats and "by_setup" not in _stats:
    # Migrate from the old per-exact-filename scheme: every setup version bump
    # (e.g. HYMO 1.3.1 -> 1.3.2) created a brand new key, so counts never
    # accumulated for what is really the same setup and the file just grew
    # forever. The new scheme keys on (car, track, author), which stays stable
    # across version updates. Lifetime total is preserved; per-setup history
    # restarts clean since the old keys can't be reliably mapped to a car.
    _stats = {"total_downloads": _stats.get("total_downloads", 0), "by_setup": {}}
    _save(_STATS_FILE, _stats)


def get_game_version() -> str:
    return _settings.get("game_version", "")


def set_game_version(version: str) -> None:
    with _lock:
        _settings["game_version"] = version.strip()
        _save(_SETTINGS_FILE, _settings)


def get_admin_ids() -> set[int]:
    """ADMIN_IDS from .env (the fixed bootstrap set, always kept — this is what
    protects against ever locking yourself out) plus admins added at runtime
    via the bot's /addadmin command (persisted, so they survive restarts and
    are independent per-deployment)."""
    return ADMIN_IDS | {int(x) for x in _admins.get("extra_ids", [])}


def is_admin(user_id: int) -> bool:
    return user_id in get_admin_ids()


def add_admin(user_id: int) -> bool:
    """Returns False if user_id was already an admin (env or extra)."""
    if user_id in get_admin_ids():
        return False
    with _lock:
        ids = set(_admins.get("extra_ids", []))
        ids.add(user_id)
        _admins["extra_ids"] = sorted(ids)
        _save(_ADMINS_FILE, _admins)
    return True


def remove_admin(user_id: int) -> bool:
    """Only removes runtime-added admins — .env ADMIN_IDS can't be revoked
    from the bot itself, only by editing .env, so you can never lock yourself
    out entirely. Returns False if user_id wasn't a runtime admin."""
    with _lock:
        ids = set(_admins.get("extra_ids", []))
        if user_id not in ids:
            return False
        ids.discard(user_id)
        _admins["extra_ids"] = sorted(ids)
        _save(_ADMINS_FILE, _admins)
    return True


def get_lang(user_id: int) -> str | None:
    u = _users.get(str(user_id))
    return u.get("lang") if u else None


def set_lang(user_id: int, lang: str) -> None:
    with _lock:
        _users.setdefault(str(user_id), {})["lang"] = lang
        _save(_USERS_FILE, _users)


def count_users() -> int:
    return len(_users)


def record_download(car: str, track: str, author: str) -> None:
    """Count a download under its (car, track, author) identity — stable across
    setup version bumps, unlike the exact filename which changes every update."""
    with _lock:
        key = f"{car}|{track}|{author}"
        entry = _stats.setdefault("by_setup", {}).setdefault(
            key, {"car": car, "track": track, "author": author, "count": 0}
        )
        entry["count"] += 1
        _stats["total_downloads"] = _stats.get("total_downloads", 0) + 1
        _save(_STATS_FILE, _stats)


def stats_summary(top: int = 10) -> tuple[int, list[tuple[str, int]]]:
    by_setup: dict[str, dict] = _stats.get("by_setup", {})
    ranked = sorted(by_setup.values(), key=lambda e: -e["count"])[:top]
    labels = [(f"{e['car']} @ {e['track']} ({e['author']})", e["count"]) for e in ranked]
    return _stats.get("total_downloads", 0), labels
