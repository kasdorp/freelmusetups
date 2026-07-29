"""All bot handlers: /start language pick, menu navigation, file delivery."""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from html import escape as html_escape

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

import storage
from catalog import car_name, track_name
from config import BASE_DIR
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
    if not storage.is_admin(message.from_user.id):
        return
    snap = get_snapshot(force=True)
    await message.answer(f"♻️ Library reloaded: {len(snap.setups)} setups.")


@router.message(Command("newsetups"))
async def cmd_newsetups(message: Message) -> None:
    """Broadcast to every user who has ever /start-ed the bot about setups
    added since the last time this command ran. First run just records the
    current library as the baseline (no broadcast) — otherwise the very first
    call would blast the entire existing library at everyone."""
    if not storage.is_admin(message.from_user.id):
        return
    snap = get_snapshot(force=True)
    current_ids = {s.id: s for s in snap.setups}

    if not storage.has_announced_baseline():
        storage.mark_announced(set(current_ids))
        await message.answer(
            f"ℹ️ First run — baseline set with the current {len(current_ids)} setups. "
            f"Nothing was announced. Next time, only what's new since now will be sent."
        )
        return

    new_ids = set(current_ids) - storage.get_announced_ids()
    if not new_ids:
        await message.answer("ℹ️ No new setups since the last announcement.")
        return

    new_setups = [current_ids[i] for i in new_ids]
    combos = sorted({(s.car_name, track_name(s.track), s.author) for s in new_setups})
    max_lines = 40
    lines = [f"🏎 {car} @ {track} ({author})" for car, track, author in combos[:max_lines]]
    extra = len(combos) - max_lines

    sent = failed = 0
    for uid in storage.get_all_user_ids():
        lang = storage.get_lang(uid) or "en"
        body = "\n".join(lines)
        if extra > 0:
            body += "\n" + t(lang, "newsetups_more", n=extra)
        text = t(lang, "newsetups_header") + "\n\n" + body + t(lang, "newsetups_footer")
        try:
            await message.bot.send_message(uid, text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    storage.mark_announced(new_ids)
    await message.answer(
        f"✅ Announced {len(combos)} new setup(s) ({len(new_setups)} files) to {sent} users "
        f"({failed} failed/blocked the bot)."
    )


@router.message(Command("update"))
async def cmd_update(message: Message) -> None:
    """git pull the deployment this process is running on, then restart into
    the freshly pulled code. Meant for the server deployment — lets you push
    code/setups from your PC and roll it out to the server via one Telegram
    command instead of RDP-ing in."""
    if not storage.is_admin(message.from_user.id):
        return
    await message.answer("🔄 Running git pull...")
    result = subprocess.run(
        ["git", "pull", "--ff-only"],
        cwd=BASE_DIR, capture_output=True, text=True,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        await message.answer(f"❌ git pull failed:\n<code>{html_escape(output[:1500])}</code>")
        return
    if "up to date" in output.lower():
        await message.answer(f"✅ Already up to date.\n<code>{html_escape(output[:500])}</code>")
        return
    await message.answer(f"📥 Updated:\n<code>{html_escape(output[:1500])}</code>\n\n♻️ Restarting...")
    await message.bot.session.close()
    os.execv(sys.executable, [sys.executable] + sys.argv)


@router.message(Command("setversion"))
async def cmd_setversion(message: Message) -> None:
    if not storage.is_admin(message.from_user.id):
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


@router.message(Command("admins"))
async def cmd_admins(message: Message) -> None:
    if not storage.is_admin(message.from_user.id):
        return
    ids = sorted(storage.get_admin_ids())
    await message.answer(
        "👑 Admins:\n" + "\n".join(f"  <code>{i}</code>" for i in ids)
        + "\n\nAdd: <code>/addadmin 123456789</code>\nRemove: <code>/removeadmin 123456789</code>"
    )


@router.message(Command("addadmin"))
async def cmd_addadmin(message: Message) -> None:
    if not storage.is_admin(message.from_user.id):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        await message.answer("Usage: <code>/addadmin 123456789</code> (the user's Telegram ID, e.g. from /id)")
        return
    new_id = int(parts[1].strip())
    if storage.add_admin(new_id):
        await message.answer(f"✅ <code>{new_id}</code> is now an admin.")
    else:
        await message.answer(f"ℹ️ <code>{new_id}</code> was already an admin.")


@router.message(Command("removeadmin"))
async def cmd_removeadmin(message: Message) -> None:
    if not storage.is_admin(message.from_user.id):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        await message.answer("Usage: <code>/removeadmin 123456789</code>")
        return
    old_id = int(parts[1].strip())
    if storage.remove_admin(old_id):
        await message.answer(f"✅ <code>{old_id}</code> is no longer an admin.")
    else:
        await message.answer(
            f"⚠️ <code>{old_id}</code> isn't a removable admin — either not an admin, "
            f"or set via ADMIN_IDS in .env (edit .env directly to change those)."
        )


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    if not storage.is_admin(message.from_user.id):
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
