"""English / Russian texts for the bot UI."""

TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "choose_lang": "👋 Welcome to <b>LMU Setup Bot</b>!\n\nChoose your language:",
        "lang_saved": "✅ Language set: English",
        "main_menu": (
            "🏁 <b>Le Mans Ultimate — Setup Bot</b>\n\n"
            "Free car setups for LMU, always up to date.\n"
            "Pick a car → track → setup maker, and get the file in seconds.\n"
            "{version_line}\n"
            "📦 In the library right now: <b>{n_setups}</b> setups • "
            "<b>{n_cars}</b> cars • <b>{n_tracks}</b> tracks"
        ),
        "version_line": "\n🎮 Setups for game version: <b>{v}</b>\n",
        "btn_get": "🔧 Get a setup",
        "btn_help": "📥 How to install",
        "btn_about": "ℹ️ About",
        "btn_lang": "🌐 Language",
        "btn_back": "⬅️ Back",
        "btn_home": "🏠 Main menu",
        "choose_class": "🚗 <b>Step 1/4.</b> Choose a car class:",
        "choose_car": "🚗 <b>Step 2/4.</b> Choose your car ({cls}):",
        "choose_track": "📍 <b>Step 3/4.</b> Choose a track for <b>{car}</b>:",
        "choose_author": "👨‍🔧 <b>Step 4/4.</b> Choose a setup maker for <b>{car}</b> @ <b>{track}</b>:",
        "choose_file": (
            "📄 Setups by <b>{author}</b> — <b>{car}</b> @ <b>{track}</b>\n\n"
            "⏱ = qualifying • 🏁 = race\nTap one to download:"
        ),
        "file_caption": (
            "🏎 <b>{car}</b>\n📍 {track}\n👨‍🔧 {author}\n\n"
            "📥 Put this file into:\n<code>...\\Le Mans Ultimate\\UserData\\player\\Settings\\{track_folder}\\</code>\n"
            "then in game: Garage → Setup → load it. GL &amp; HF! 🏁"
        ),
        "no_setups": "😔 Nothing here yet — new setups are added regularly, check back soon!",
        "empty_library": "😔 The setup library is empty right now. Check back soon!",
        "menu_outdated": "♻️ This menu is outdated (library was updated). Here is a fresh one:",
        "install_help": (
            "📥 <b>How to install a setup</b>\n\n"
            "1️⃣ Download the <code>.svm</code> file from this bot\n"
            "2️⃣ Copy it to the track folder:\n"
            "<code>C:\\Program Files (x86)\\Steam\\steamapps\\common\\Le Mans Ultimate\\UserData\\player\\Settings\\&lt;Track&gt;\\</code>\n"
            "   (the bot tells you the exact track folder with every file)\n"
            "3️⃣ Launch LMU, enter a session on that track\n"
            "4️⃣ Garage → <b>Setup</b> → select the setup → <b>Load</b>\n\n"
            "💡 The folder for a track appears after you visit it once in game — "
            "or just create it yourself with exactly the same name."
        ),
        "about": (
            "ℹ️ <b>LMU Setup Bot</b>\n\n"
            "Free community setups for Le Mans Ultimate.\n"
            "{version_line}"
            "📦 Setups: <b>{n_setups}</b>\n🚗 Cars: <b>{n_cars}</b>\n📍 Tracks: <b>{n_tracks}</b>\n"
            "👨‍🔧 Setup makers: <b>{n_authors}</b>\n\n"
            "The library updates automatically — new files appear in the bot instantly.\n\n"
            "💬 Ideas, suggestions, new setups — dev: @unjsxx128"
        ),
        "btn_contact": "💬 Message the developer",
    },
    "ru": {
        "choose_lang": "👋 Добро пожаловать в <b>LMU Setup Bot</b>!\n\nВыберите язык:",
        "lang_saved": "✅ Язык выбран: Русский",
        "main_menu": (
            "🏁 <b>Le Mans Ultimate — бот сетапов</b>\n\n"
            "Бесплатные сетапы для LMU, всегда актуальные.\n"
            "Выбери машину → трассу → автора сетапа — и получи файл за секунды.\n"
            "{version_line}\n"
            "📦 Сейчас в библиотеке: <b>{n_setups}</b> сетапов • "
            "<b>{n_cars}</b> машин • <b>{n_tracks}</b> трасс"
        ),
        "version_line": "\n🎮 Сетапы под версию игры: <b>{v}</b>\n",
        "btn_get": "🔧 Получить сетап",
        "btn_help": "📥 Как установить",
        "btn_about": "ℹ️ О боте",
        "btn_lang": "🌐 Язык",
        "btn_back": "⬅️ Назад",
        "btn_home": "🏠 Главное меню",
        "choose_class": "🚗 <b>Шаг 1/4.</b> Выберите класс машины:",
        "choose_car": "🚗 <b>Шаг 2/4.</b> Выберите машину ({cls}):",
        "choose_track": "📍 <b>Шаг 3/4.</b> Выберите трассу для <b>{car}</b>:",
        "choose_author": "👨‍🔧 <b>Шаг 4/4.</b> Выберите автора сетапа — <b>{car}</b> @ <b>{track}</b>:",
        "choose_file": (
            "📄 Сетапы от <b>{author}</b> — <b>{car}</b> @ <b>{track}</b>\n\n"
            "⏱ = квалификация • 🏁 = гонка\nНажмите, чтобы скачать:"
        ),
        "file_caption": (
            "🏎 <b>{car}</b>\n📍 {track}\n👨‍🔧 {author}\n\n"
            "📥 Положите файл в папку:\n<code>...\\Le Mans Ultimate\\UserData\\player\\Settings\\{track_folder}\\</code>\n"
            "затем в игре: Гараж → Настройки (Setup) → загрузить. Удачи на трассе! 🏁"
        ),
        "no_setups": "😔 Тут пока пусто — новые сетапы добавляются регулярно, загляните позже!",
        "empty_library": "😔 Библиотека сетапов пока пуста. Загляните позже!",
        "menu_outdated": "♻️ Это меню устарело (библиотека обновилась). Вот свежее:",
        "install_help": (
            "📥 <b>Как установить сетап</b>\n\n"
            "1️⃣ Скачайте файл <code>.svm</code> из этого бота\n"
            "2️⃣ Скопируйте его в папку трассы:\n"
            "<code>C:\\Program Files (x86)\\Steam\\steamapps\\common\\Le Mans Ultimate\\UserData\\player\\Settings\\&lt;Трасса&gt;\\</code>\n"
            "   (точное имя папки бот присылает вместе с каждым файлом)\n"
            "3️⃣ Запустите LMU и зайдите в сессию на этой трассе\n"
            "4️⃣ Гараж → <b>Setup</b> → выберите сетап → <b>Load</b>\n\n"
            "💡 Папка трассы появляется после первого захода на неё в игре — "
            "или просто создайте её вручную с точно таким же названием."
        ),
        "about": (
            "ℹ️ <b>LMU Setup Bot</b>\n\n"
            "Бесплатные сетапы сообщества для Le Mans Ultimate.\n"
            "{version_line}"
            "📦 Сетапов: <b>{n_setups}</b>\n🚗 Машин: <b>{n_cars}</b>\n📍 Трасс: <b>{n_tracks}</b>\n"
            "👨‍🔧 Авторов: <b>{n_authors}</b>\n\n"
            "Библиотека обновляется автоматически — новые файлы появляются в боте мгновенно.\n\n"
            "💬 Идеи, предложения, новые сетапы — dev: @unjsxx128"
        ),
        "btn_contact": "💬 Написать разработчику",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in TEXTS else "en"
    text = TEXTS[lang].get(key) or TEXTS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text
