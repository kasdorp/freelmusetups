"""All bot handlers: /start language pick, menu navigation, file delivery."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

import storage
from catalog import car_name, track_name
from config import ADMIN_IDS
from i18n import t
from keyboards import (kb_authors, kb_cars, kb_classes, kb_files, kb_language,
                       kb_main, kb_tracks, nav_row, resolve)
from library import get_snapshot

router = Router()


def user_lang(user_id: int) -> str | None:
    return storage.get_lang(user_id)


def library_counts() -> dict:
    snap = get_snapshot()
    return {
        "n_setups": len(snap.setups),
        "n_cars": len({s.car for s in snap.setups}),
        "n_tracks": len({s.track for s in snap.setups}),
        "n_authors": len({s.author for s in snap.setups}),
    }


def version_line(lang: str) -> str:
    v = storage.get_game_version()
    return t(lang, "version_line", v=v) if v else ""


async def show_main_menu(message: Message, lang: str, edit: bool = False) -> None:
    counts = {k: v for k, v in library_counts().items() if k != "n_authors"}
    text = t(lang, "main_menu", version_line=version_line(lang), **counts)
    if edit:
        await message.edit_text(text, reply_markup=kb_main(lang))
    else:
        await message.answer(text, reply_markup=kb_main(lang))


# ---- start / language -----------------------------------------------------

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(t("en", "choose_lang"), reply_markup=kb_language())


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    lang = user_lang(message.from_user.id)
    if lang is None:
        await message.answer(t("en", "choose_lang"), reply_markup=kb_language())
    else:
        await show_main_menu(message, lang)


@router.callback_query(F.data.startswith("lang|"))
async def cb_lang(cb: CallbackQuery) -> None:
    lang = cb.data.split("|", 1)[1]
    storage.set_lang(cb.from_user.id, lang)
    await cb.answer(t(lang, "lang_saved"))
    await show_main_menu(cb.message, lang, edit=True)


@router.callback_query(F.data == "langmenu")
async def cb_langmenu(cb: CallbackQuery) -> None:
    await cb.message.edit_text(t("en", "choose_lang"), reply_markup=kb_language())
    await cb.answer()


# ---- static pages ---------------------------------------------------------

@router.callback_query(F.data == "home")
async def cb_home(cb: CallbackQuery) -> None:
    lang = user_lang(cb.from_user.id) or "en"
    await show_main_menu(cb.message, lang, edit=True)
    await cb.answer()


@router.callback_query(F.data == "help")
async def cb_help(cb: CallbackQuery) -> None:
    lang = user_lang(cb.from_user.id) or "en"
    kb = InlineKeyboardMarkup(inline_keyboard=[nav_row(lang, None)])
    await cb.message.edit_text(t(lang, "install_help"), reply_markup=kb)
    await cb.answer()


DEV_CONTACT_URL = "https://t.me/unjsxx128"


@router.callback_query(F.data == "about")
async def cb_about(cb: CallbackQuery) -> None:
    lang = user_lang(cb.from_user.id) or "en"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_contact"), url=DEV_CONTACT_URL)],
        nav_row(lang, None),
    ])
    await cb.message.edit_text(
        t(lang, "about", version_line=version_line(lang), **library_counts()),
        reply_markup=kb,
    )
    await cb.answer()


# ---- setup browsing: class -> car -> track -> author -> file --------------

@router.callback_query(F.data == "get")
async def cb_get(cb: CallbackQuery) -> None:
    lang = user_lang(cb.from_user.id) or "en"
    snap = get_snapshot()
    if not snap.setups:
        await cb.answer(t(lang, "empty_library"), show_alert=True)
        return
    await cb.message.edit_text(t(lang, "choose_class"), reply_markup=kb_classes(snap, lang))
    await cb.answer()


@router.callback_query(F.data.startswith("cls|"))
async def cb_class(cb: CallbackQuery) -> None:
    lang = user_lang(cb.from_user.id) or "en"
    cls = cb.data.split("|", 1)[1]
    snap = get_snapshot()
    await cb.message.edit_text(t(lang, "choose_car", cls=cls), reply_markup=kb_cars(snap, lang, cls))
    await cb.answer()


async def _outdated(cb: CallbackQuery, lang: str) -> None:
    """Selected item vanished after a library update — show a fresh menu."""
    snap = get_snapshot(force=True)
    await cb.message.edit_text(
        t(lang, "menu_outdated") + "\n\n" + t(lang, "choose_class"),
        reply_markup=kb_classes(snap, lang),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("car|"))
async def cb_car(cb: CallbackQuery) -> None:
    lang = user_lang(cb.from_user.id) or "en"
    _, cls, car_h = cb.data.split("|")
    snap = get_snapshot()
    car = resolve(snap, "car", car_h)
    if car is None:
        return await _outdated(cb, lang)
    await cb.message.edit_text(
        t(lang, "choose_track", car=car_name(car)),
        reply_markup=kb_tracks(snap, lang, cls, car),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("trk|"))
async def cb_track(cb: CallbackQuery) -> None:
    lang = user_lang(cb.from_user.id) or "en"
    _, cls, car_h, trk_h = cb.data.split("|")
    snap = get_snapshot()
    car = resolve(snap, "car", car_h)
    track = resolve(snap, "track", trk_h)
    if car is None or track is None:
        return await _outdated(cb, lang)
    await cb.message.edit_text(
        t(lang, "choose_author", car=car_name(car), track=track_name(track)),
        reply_markup=kb_authors(snap, lang, cls, car, track),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("aut|"))
async def cb_author(cb: CallbackQuery) -> None:
    lang = user_lang(cb.from_user.id) or "en"
    _, cls, car_h, trk_h, aut_h = cb.data.split("|")
    snap = get_snapshot()
    car = resolve(snap, "car", car_h)
    track = resolve(snap, "track", trk_h)
    author = resolve(snap, "author", aut_h)
    if car is None or track is None or author is None:
        return await _outdated(cb, lang)
    await cb.message.edit_text(
        t(lang, "choose_file", author=author, car=car_name(car), track=track_name(track)),
        reply_markup=kb_files(snap, lang, cls, car, track, author),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("f|"))
async def cb_file(cb: CallbackQuery) -> None:
    lang = user_lang(cb.from_user.id) or "en"
    setup_id = cb.data.split("|", 1)[1]
    snap = get_snapshot()
    setup = snap.by_id.get(setup_id)
    if setup is None or not setup.path.is_file():
        return await _outdated(cb, lang)
    await cb.answer("📥 ...")
    caption = t(
        lang, "file_caption",
        car=setup.car_name,
        track=track_name(setup.track),
        author=setup.author,
        track_folder=setup.track,
    )
    await cb.message.answer_document(FSInputFile(setup.path), caption=caption)
    storage.record_download(car=setup.car_name, track=setup.track, author=setup.author)


# ---- admin ----------------------------------------------------------------

@router.message(Command("id"))
async def cmd_id(message: Message) -> None:
    await message.answer(f"Your Telegram ID: <code>{message.from_user.id}</code>")


@router.message(Command("reload"))
async def cmd_reload(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    snap = get_snapshot(force=True)
    await message.answer(f"♻️ Library reloaded: {len(snap.setups)} setups.")


@router.message(Command("setversion"))
async def cmd_setversion(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        current = storage.get_game_version() or "—"
        await message.answer(
            f"🎮 Current game version: <b>{current}</b>\n"
            f"Set a new one: <code>/setversion 1.3.4</code>"
        )
        return
    storage.set_game_version(parts[1])
    await message.answer(f"✅ Game version set: <b>{parts[1].strip()}</b>")


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if message.from_user.id not in ADMIN_IDS:
        return
    snap = get_snapshot()
    total, top = storage.stats_summary()
    lines = [
        f"👥 Users: {storage.count_users()}",
        f"📦 Setups: {len(snap.setups)}",
        f"📥 Downloads: {total}",
        "",
        "🔝 Top downloads:",
    ]
    lines += [f"  {n}× — {label}" for label, n in top] or ["  —"]
    await message.answer("\n".join(lines))
