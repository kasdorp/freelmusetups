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
  "setups": [ ["<path under setups/>", "<track folder>", "<vehicle folder>", "<author>", "<Q|R|>", <size>], ... ]
}
"""
from __future__ import annotations

import json
from pathlib import Path

from catalog import car_class, car_name, track_name
from config import BASE_DIR, SETUPS_DIR
from library import get_snapshot

OUT = BASE_DIR / "setups_index.json"


def plain_size(path: Path) -> int:
    """The file's size with Windows line ends counted as one byte, the same
    whether git checked it out with CRLF (Windows) or LF (the workflow, and
    the raw files SimpleInputs downloads)."""
    return len(path.read_bytes().replace(b"\r\n", b"\n"))


def build() -> dict:
    snap = get_snapshot(force=True)
    setups = sorted(snap.setups, key=lambda s: (s.track.lower(), s.car.lower(), s.author.lower(), s.name.lower()))
    return {
        "version": 1,
        "cars": {car: [car_name(car), car_class(car)] for car in sorted({s.car for s in setups})},
        "tracks": {track: track_name(track) for track in sorted({s.track for s in setups})},
        "setups": [
            [
                s.path.relative_to(SETUPS_DIR).as_posix(),
                s.track,
                s.car,
                s.author,
                s.kind,
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
