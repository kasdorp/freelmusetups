"""Writes setups_index.json: the setup library as SimpleInputs reads it.

SimpleInputs (the overlay app) downloads setups straight from this repository
on GitHub and puts them in the game's own folder. It reads this index rather
than every file, so the car each setup belongs to is worked out here, by the
same scanner the bot uses (library.py) — the app and the bot always agree.

Run it after adding setups, or let the GitHub workflow do it on every push
(.github/workflows/index.yml), which publishes it on the "index" branch.

Format (kept small, it is fetched by every copy of the app):
{
  "version": 1,
  "cars":   { "<vehicle folder>": ["<name>", "<class>"], ... },
  "tracks": { "<track folder>": "<name>", ... },
  "folders": { "<track folder>": "<the game's folder for it>", ... },
  "setups": [ ["<path under setups/>", "<track folder>", "<vehicle folder>", "<author>", "<Q|R|E|>", <size>], ... ]
}

The kind is the bot's Q or R, and E for an endurance setup the bot shows
without one ("P1Doks_..._SafeE", "GO ... Endu Esport").
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from catalog import car_class, car_name, track_name
from config import BASE_DIR, SETUPS_DIR
from library import get_snapshot

OUT = BASE_DIR / "setups_index.json"

# Layouts the library keeps in folders of their own that the game reads from
# one: every Silverstone layout keeps its setups in Settings\Silverstone.
# A new layout folder of the same kind needs a line here, nothing in the app.
GAME_FOLDERS = {
    "Silverstonewec": "Silverstone",
    "Silverstone_International": "Silverstone",
    "Silverstone_National": "Silverstone",
}

# An endurance marker standing alone as a token, the way library.py reads Q
# and R: an optional Title-Case condition ("Safe", "Wet"), then E, Endu or
# Endurance, then optional digits or a "safe" suffix. Case-sensitive, so
# ALL-CAPS abbreviations ("ELMS", "EVO2") and words like "Esport" are left out.
_ENDURANCE_RE = re.compile(
    r"(?:^|[\s_\-.])(?:[A-Z][a-z]*)?(?:E|Endu(?:rance)?)\d*(?:safe)?(?=$|[\s_\-.])"
)


def plain_size(path: Path) -> int:
    """The file's size with Windows line ends counted as one byte, the same
    whether git checked it out with CRLF (Windows) or LF (the workflow, and
    the raw files SimpleInputs downloads)."""
    return len(path.read_bytes().replace(b"\r\n", b"\n"))


# For the few names the bot reads no kind in at all, a looser reading: a
# lower-case condition ("wetR"), the marker in capitals ("ENDU"), or a version
# after it ("QV2"). The rightmost match wins, as in library.py.
_LOOSE_RE = re.compile(
    r"(?:^|[\s_\-.])(?:[A-Z][a-z]*|wet|safe)?"
    r"(?P<code>Q(?:uali)?|R(?:ace)?|E|Endu(?:rance)?|ENDU(?:RANCE)?)\d*(?:V\d+)?(?:safe)?(?=$|[\s_\-.])"
)


def kind_of(kind: str, name: str) -> str:
    if kind:
        return kind
    if _ENDURANCE_RE.search(name):
        return "E"
    matches = list(_LOOSE_RE.finditer(name))
    return matches[-1].group("code")[0].upper() if matches else ""


def build() -> dict:
    snap = get_snapshot(force=True)
    setups = sorted(snap.setups, key=lambda s: (s.track.lower(), s.car.lower(), s.author.lower(), s.name.lower()))

    # One author written two ways ("P1Doks" and "P1doks") is one author:
    # the spelling most of their files use.
    spellings: dict[str, Counter] = {}
    for s in setups:
        spellings.setdefault(s.author.lower(), Counter())[s.author] += 1
    author = {low: counts.most_common(1)[0][0] for low, counts in spellings.items()}

    return {
        "version": 1,
        "cars": {car: [car_name(car), car_class(car)] for car in sorted({s.car for s in setups})},
        "tracks": {track: track_name(track) for track in sorted({s.track for s in setups})},
        "folders": {track: GAME_FOLDERS[track] for track in sorted({s.track for s in setups}) if track in GAME_FOLDERS},
        "setups": [
            [
                s.path.relative_to(SETUPS_DIR).as_posix(),
                s.track,
                s.car,
                author[s.author.lower()],
                kind_of(s.kind, s.name),
                plain_size(s.path),
            ]
            for s in setups
        ],
    }


def main() -> None:
    index = build()
    text = json.dumps(index, ensure_ascii=False, separators=(",", ":"))
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if text != old:
        OUT.write_text(text, encoding="utf-8")
    print(f"{len(index['setups'])} setups, {len(index['cars'])} cars, {len(index['tracks'])} tracks"
          f"{'' if text != old else ' (unchanged)'} -> {Path(OUT).name}")


if __name__ == "__main__":
    main()
