"""Setup library scanner.

The library is just a folder tree mirroring the game:

    setups/<TrackFolder>/file.svm            (author = first word of filename)
    setups/<TrackFolder>/<Author>/file.svm   (author = subfolder name)

Every .svm declares the car it belongs to (//VEH= line), so the car is
detected automatically — drop a file in and it shows up in the bot within
LIBRARY_CACHE_TTL seconds, no code changes, no restart.
"""
from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from catalog import car_class, car_name
from config import LIBRARY_CACHE_TTL, SETUPS_DIR

_VEH_RE = re.compile(r"Installed[\\/]+Vehicles[\\/]+([^\\/\r\n]+)", re.IGNORECASE)
_CLASS_RE = re.compile(r'VehicleClassSetting\s*=\s*"([^"]*)"', re.IGNORECASE)

# Session-code token: an optional condition prefix, then Q/R (bare letter or
# the Title-Case word "Quali"/"Race"), then optional digits and/or a lowercase
# "safe" condition suffix, standing alone as a whole token — e.g. "Q", "R01",
# "EQ", "ER", "CQ", "WR", "SafeQ", "WetR", "Quali", "Race", "Qsafe", "Rsafe".
# The prefix must be a single uppercase letter optionally followed by
# lowercase ones (Title-Case word shape: "C", "W", "Safe", "Wet"...) —
# deliberately case-sensitive, so ALL-CAPS car/track abbreviations that
# happen to contain Q/R ("HUR", "RCF", "BAR") don't get mistaken for session
# codes. The suffix is kept to the one observed word ("safe") rather than any
# lowercase run — a generic `[a-z]*` here would also swallow track names like
# "Qatar" (Q + "atar"), misreading them as quali markers.
_SESSION_RE = re.compile(
    r"(?:^|[\s_\-.])(?:[A-Z][a-z]*)?(?P<code>Q(?:uali)?|R(?:ace)?)\d*(?:safe)?(?=$|[\s_\-.])"
)


@dataclass
class Setup:
    id: str            # short stable id (hash of relative path) used in callbacks
    path: Path
    name: str          # filename without extension
    track: str         # track folder name (game convention)
    car: str           # vehicle folder name
    author: str
    kind: str          # "Q", "R" or ""
    mtime: float

    @property
    def car_name(self) -> str:
        return car_name(self.car)

    @property
    def car_class(self) -> str:
        return car_class(self.car)


@dataclass
class Snapshot:
    setups: list[Setup] = field(default_factory=list)
    by_id: dict[str, Setup] = field(default_factory=dict)
    scanned_at: float = 0.0


def _short_id(rel_path: str) -> str:
    return hashlib.sha1(rel_path.encode("utf-8", "replace")).hexdigest()[:10]


def _detect_car(path: Path) -> str | None:
    """Read the header of a .svm and return the vehicle folder name."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            head = f.read(4096)
    except OSError:
        return None
    m = _VEH_RE.search(head)
    if m:
        return m.group(1).strip()
    # fallback: try to match a VehicleClassSetting token against known cars
    m = _CLASS_RE.search(head)
    if m:
        from catalog import CARS
        tokens = m.group(1).split()
        for folder in CARS:
            for tok in tokens:
                if tok.lower() in folder.lower() or folder.lower() in tok.lower():
                    return folder
    return None


def _detect_author(path: Path, track_dir: Path) -> str:
    """Author = subfolder name if nested, else first word of the filename."""
    if path.parent != track_dir:
        return path.parent.name
    stem = path.stem
    token = re.split(r"[\s_]+", stem.strip(), maxsplit=1)[0]
    return token if token else "Unknown"


def _detect_kind(stem: str) -> str:
    """"Q" or "R" from the last session-code token in the name, e.g. the "WQ"
    in "HYMO 1.3.1 RCF BAR WQ" — the session marker is conventionally the last
    token, so the rightmost match wins over incidental letters earlier in the
    name (car/track abbreviations, version numbers, etc.)."""
    matches = list(_SESSION_RE.finditer(stem))
    if not matches:
        return ""
    code = matches[-1].group("code")
    return "Q" if code[0].upper() == "Q" else "R"


# ---------------------------------------------------------------------------

_parse_cache: dict[str, tuple[float, int, Setup]] = {}   # rel_path -> (mtime, size, Setup)
_snapshot: Snapshot = Snapshot()


def _scan() -> Snapshot:
    snap = Snapshot(scanned_at=time.time())
    root = SETUPS_DIR
    if not root.is_dir():
        return snap
    for track_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        if track_dir.name.startswith("_"):
            continue  # folders prefixed with "_" are excluded from the bot
        for path in sorted(track_dir.rglob("*.svm")):
            # any file or parent folder prefixed with "_" is excluded
            rel_parts = path.relative_to(track_dir).parts
            if any(part.startswith("_") for part in rel_parts):
                continue
            rel = str(path.relative_to(root))
            try:
                st = path.stat()
            except OSError:
                continue
            cached = _parse_cache.get(rel)
            if cached and cached[0] == st.st_mtime and cached[1] == st.st_size:
                setup = cached[2]
            else:
                car = _detect_car(path)
                if not car:
                    continue  # unreadable / not a real setup file
                setup = Setup(
                    id=_short_id(rel),
                    path=path,
                    name=path.stem,
                    track=track_dir.name,
                    car=car,
                    author=_detect_author(path, track_dir),
                    kind=_detect_kind(path.stem),
                    mtime=st.st_mtime,
                )
                _parse_cache[rel] = (st.st_mtime, st.st_size, setup)
            snap.setups.append(setup)
            snap.by_id[setup.id] = setup
    return snap


def get_snapshot(force: bool = False) -> Snapshot:
    """Return the current library, rescanning at most every LIBRARY_CACHE_TTL s."""
    global _snapshot
    if force or time.time() - _snapshot.scanned_at > LIBRARY_CACHE_TTL:
        _snapshot = _scan()
    return _snapshot


# ---- query helpers used by the menus --------------------------------------

def classes(snap: Snapshot) -> dict[str, int]:
    """Car classes that actually have setups -> setup count."""
    out: dict[str, int] = {}
    for s in snap.setups:
        out[s.car_class] = out.get(s.car_class, 0) + 1
    return out


def cars_in_class(snap: Snapshot, cls: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for s in snap.setups:
        if s.car_class == cls:
            out[s.car] = out.get(s.car, 0) + 1
    return out


def tracks_for_car(snap: Snapshot, car: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for s in snap.setups:
        if s.car == car:
            out[s.track] = out.get(s.track, 0) + 1
    return out


def authors_for(snap: Snapshot, car: str, track: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for s in snap.setups:
        if s.car == car and s.track == track:
            out[s.author] = out.get(s.author, 0) + 1
    return out


def files_for(snap: Snapshot, car: str, track: str, author: str) -> list[Setup]:
    items = [s for s in snap.setups if s.car == car and s.track == track and s.author == author]
    items.sort(key=lambda s: (-s.mtime, s.name.lower()))
    return items
