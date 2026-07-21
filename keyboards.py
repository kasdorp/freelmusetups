"""Inline keyboards. Callback data carries short stable hashes so it always
fits Telegram's 64-byte limit regardless of file/author names."""
from __future__ import annotations

import hashlib

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from catalog import CLASS_EMOJI, CLASS_ORDER, car_name, track_name
from i18n import t
from library import Snapshot, authors_for, cars_in_class, classes, files_for, tracks_for_car


def h(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()[:10]


def resolve(snap: Snapshot, kind: str, hashed: str) -> str | None:
    """Map a short hash back to the car/track/author it stands for."""
    values: set[str] = set()
    for s in snap.setups:
        if kind == "car":
            values.add(s.car)
        elif kind == "track":
            values.add(s.track)
        elif kind == "author":
            values.add(s.author)
    for v in values:
        if h(v) == hashed:
            return v
    return None


def nav_row(lang: str, back_cb: str | None) -> list[InlineKeyboardButton]:
    row = []
    if back_cb:
        row.append(InlineKeyboardButton(text=t(lang, "btn_back"), callback_data=back_cb))
    row.append(InlineKeyboardButton(text=t(lang, "btn_home"), callback_data="home"))
    return row


def kb_language() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang|en"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang|ru"),
    ]])


def kb_main(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t(lang, "btn_get"), callback_data="get"))
    b.row(
        InlineKeyboardButton(text=t(lang, "btn_help"), callback_data="help"),
        InlineKeyboardButton(text=t(lang, "btn_about"), callback_data="about"),
    )
    b.row(InlineKeyboardButton(text=t(lang, "btn_lang"), callback_data="langmenu"))
    return b.as_markup()


def kb_classes(snap: Snapshot, lang: str) -> InlineKeyboardMarkup:
    counts = classes(snap)
    b = InlineKeyboardBuilder()
    for cls in CLASS_ORDER:
        if cls in counts:
            b.row(InlineKeyboardButton(
                text=f"{CLASS_EMOJI.get(cls, '')} {cls}  ({counts[cls]})",
                callback_data=f"cls|{cls}",
            ))
    b.row(*nav_row(lang, "home"))
    return b.as_markup()


def kb_cars(snap: Snapshot, lang: str, cls: str) -> InlineKeyboardMarkup:
    counts = cars_in_class(snap, cls)
    b = InlineKeyboardBuilder()
    for folder in sorted(counts, key=lambda f: car_name(f).lower()):
        b.row(InlineKeyboardButton(
            text=f"{car_name(folder)}  ({counts[folder]})",
            callback_data=f"car|{cls}|{h(folder)}",
        ))
    b.row(*nav_row(lang, "get"))
    return b.as_markup()


def kb_tracks(snap: Snapshot, lang: str, cls: str, car: str) -> InlineKeyboardMarkup:
    counts = tracks_for_car(snap, car)
    b = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=f"{track_name(folder)}  ({counts[folder]})",
            callback_data=f"trk|{cls}|{h(car)}|{h(folder)}",
        )
        for folder in sorted(counts, key=lambda f: track_name(f).lower())
    ]
    for i in range(0, len(buttons), 2):
        b.row(*buttons[i:i + 2])
    b.row(*nav_row(lang, f"cls|{cls}"))
    return b.as_markup()


def kb_authors(snap: Snapshot, lang: str, cls: str, car: str, track: str) -> InlineKeyboardMarkup:
    counts = authors_for(snap, car, track)
    b = InlineKeyboardBuilder()
    for author in sorted(counts, key=str.lower):
        b.row(InlineKeyboardButton(
            text=f"👨‍🔧 {author}  ({counts[author]})",
            callback_data=f"aut|{cls}|{h(car)}|{h(track)}|{h(author)}",
        ))
    b.row(*nav_row(lang, f"car|{cls}|{h(car)}"))
    return b.as_markup()


def kb_files(snap: Snapshot, lang: str, cls: str, car: str, track: str, author: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for s in files_for(snap, car, track, author):
        tag = {"Q": "⏱ ", "R": "🏁 "}.get(s.kind, "📄 ")
        b.row(InlineKeyboardButton(text=f"{tag}{s.name}", callback_data=f"f|{s.id}"))
    b.row(*nav_row(lang, f"trk|{cls}|{h(car)}|{h(track)}"))
    return b.as_markup()
