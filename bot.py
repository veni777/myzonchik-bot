import asyncio
import json
import os
import re
import uuid
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from shazamio import Shazam
import yt_dlp

# --- НАЛАШТУВАННЯ ---
BOT_TOKEN = "9005860940:AAHUmqZuXnRrtPVBBpEOXhBbXlMtE8DVIPQ"
BOT_USERNAME = "Myzonchik_ua_bot"
USERS_FILE = "activated_users.json"
# --------------------

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
shazam = Shazam()

os.makedirs("downloads", exist_ok=True)

# Завантаження та збереження бази активованих користувачів
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                return set(json.load(f))
            except:
                return set()
    return set()

def save_users(users_set):
    with open(USERS_FILE, "w") as f:
        json.dump(list(users_set), f)

activated_users = load_users()

# Список треків для Топ-10 TikTok
TIKTOK_TOP_10 = [
    {"title": "Miyagi & Эндшпиль", "query": "Miyagi Endspiel Колибри"},
    {"title": "Klavdia Petrivna", "query": "Клавдія Петрівна Зінедін Зідан"},
    {"title": "The Weeknd", "query": "The Weeknd Timeless"},
    {"title": "Bruno Mars & Lady Gaga", "query": "Lady Gaga Bruno Mars Die With A Smile"},
    {"title": "Скриптоніт", "query": "Скриптонит Положение"},
    {"title": "Billie Eilish", "query": "Billie Eilish BIRDS OF A FEATHER"},
    {"title": "LXST CXNTURY", "query": "LXST CXNTURY ODIUM"},
    {"title": "DVRST", "query": "DVRST Close Eyes"},
    {"title": "Макс Корж", "query": "Макс Корж Жить в кайф"},
    {"title": "Imagine Dragons", "query": "Imagine Dragons Eyes Closed"}
]

def download_audio_from_url(url: str, output_path: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Перевірка: чи активував користувач бота в особистих повідомленнях
async def check_user_active(event: types.Message) -> bool:
    if event.chat.type == "channel":
        return True
        
    if event.chat.type == "private":
        if event.from_user and event.from_user.id not in activated_users:
            activated_users.add(event.from_user.id)
            save_users(activated_users)
        return True

    if event.from_user:
        if event.from_user.id in activated_users:
            return True
        else:
            await event.answer(
                f"❌ Привіт, {event.from_user.first_name}!\n"
                f"Щоб користуватися ботом у чатах, спочатку активуй його в особистих повідомленнях.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🤖 Активувати бота (Натиснути Start)", url=f"https://t.me/{BOT_USERNAME}?start=activate")]
                ]),
                parse_mode="Markdown"
            )
            return False
    return True

# 🎛 ГОЛОВНЕ МЕНЮ (працює ТІЛЬКИ в особистих повідомленнях)
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥 Топ-10 TikTok", callback_data="top_tiktok"),
            InlineKeyboardButton(text="🔍 Як шукати?", callback_data="help_search")
        ],
        [
            InlineKeyboardButton(text="➕ Додати в групу/канал", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ]
    ])

@dp.message(CommandStart())
@dp.message(Command("menu"))
async def cmd_start(message: types.Message):
    if message.from_user:
        activated_users.add(message.from_user.id)
        save_users(activated_users)

    if message.chat.type != "private":
        await message.answer("👋 Привіт! Щоб відкрити музичне меню та скористатися всіма функціями, перейди в особисті повідомлення з ботом.")
        return

    welcome_text = (
        "🎧 **Вітаю у Music Bot!**\n\n"
        "Я твій особистий музичний помічник. Що я вмію:\n"
        "• Розпізнавати треки з **TikTok, Reels та YouTube Shorts** (просто кинь посилання);\n"
        "• Шукати пісні за запитом у чаті (наприклад: `знайди Мияги колибри`);\n"
        "• Показувати найпопулярніші треки з TikTok!\n\n"
        "Обери потрібну опцію в меню нижче 👇"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "help_search")
async def callback_help(callback: types.CallbackQuery):
    help_text = (
        "💡 **Як користуватися пошуком:**\n\n"
        "1️⃣ **У особистих повідомленнях:** просто напиши назву пісні чи виконавця (або почни зі слів `знайди`, `найти`).\n"
        "2️⃣ **У груповому чаті:** пиши команду чітко:\n"
        "   👉 `знайди [назва треку]`\n"
        "3️⃣ **Завантаження з соцмереж:** просто кинь посилання на TikTok чи Reels у чат, де є бот!"
    )
    await callback.message.edit_text(help_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад у меню", callback_data="back_to_menu")]
    ]), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "back_to_menu")
async def callback_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("🎧 **Головне меню:**\nОбери дію нижче 👇", reply_markup=get_main_menu(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "top_tiktok")
async def callback_top_tiktok(callback: types.CallbackQuery):
    buttons = []
    for i, item in enumerate(TIKTOK_TOP_10, 1):
        buttons.append([InlineKeyboardButton(text=f"{i}. {item['title']}", callback_data=f"get_track_{i-1}")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад у меню", callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(
        "🔥 **Топ-10 треків із TikTok та Reels**\nНатисни на трек нижче, щоб отримати його аудіофайл:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("get_track_"))
async def callback_get_top_track(callback: types.CallbackQuery):
    index = int(callback.data.split("_")[-1])
    track_info = TIKTOK_TOP_10[index]
    query = track_info["query"]

    status_msg = await callback.message.answer(f"⏳ Завантажую трек: **{track_info['title']}**...", parse_mode="Markdown")
    
    file_id = str(uuid.uuid4())
    song_raw = f"downloads/{file_id}"
    song_mp3 = f"downloads/{file_id}.mp3"

    try:
        search_query = f"ytsearch1:{query} audio"
        await asyncio.to_thread(download_audio_from_url, search_query, song_raw)
        
        await callback.message.answer_audio(
            FSInputFile(song_mp3),
            caption=f"🔥 Трек із Топ-10 TikTok: *{track_info['title']}*",
            parse_mode="Markdown"
        )
        await status_msg.delete()
    except Exception:
        await status_msg.edit_text(f"❌ Не вдалося завантажити трек. Спробуй пізніше.")
    finally:
        if os.path.exists(song_mp3):
            os.remove(song_mp3)
    await callback.answer()

# 1. ОБРОБНИК ПОСИЛАНЬ
@dp.message(F.text.regexp(r'(https?://[^\s]+)'))
@dp.channel_post(F.text.regexp(r'(https?://[^\s]+)'))
async def handle_url(event: types.Message):
    if not await check_user_active(event):
        return

    text = event.text.strip()
    url_match = re.search(r'(https?://[^\s]+)', text)
    if not url_match:
        return
        
    url = url_match.group(1)
    status_msg = await event.answer("⏳ Завантажую звук із відео...")
    
    file_id = str(uuid.uuid4())
    raw_path = f"downloads/{file_id}"
    mp3_path = f"downloads/{file_id}.mp3"

    try:
        await asyncio.to_thread(download_audio_from_url, url, raw_path)
        
        await status_msg.edit_text("🔍 Розпізнаю трек...")
        out = await shazam.recognize(mp3_path)
        
        await process_shazam_result(event, status_msg, out, fallback_audio=mp3_path)
    except Exception as e:
        await status_msg.edit_text(f"❌ Не вдалося обробити посилання.\nПомилка: {str(e)[:100]}")
    finally:
        if os.path.exists(mp3_path):
            os.remove(mp3_path)

# 2. ОБРОБНИК ТЕКСТОВОГО ПОШУКУ
@dp.message(F.text.lower().startswith(('найти ', 'знайди ', 'пошук ', '/find ', '/search ')))
@dp.channel_post(F.text.lower().startswith(('найти ', 'знайди ', 'пошук ', '/find ', '/search ')))
async def handle_text_search(event: types.Message):
    if not await check_user_active(event):
        return

    text = event.text.strip()
    query = text
    for prefix in ['/find', '/search', 'знайди', 'найти', 'пошук']:
        if text.lower().startswith(prefix):
            query = text[len(prefix):].strip()
            break
            
    if not query:
        await event.answer("⚠️ Напиши назву пісні після запиту, наприклад:\n`знайди Мияги колибри`", parse_mode="Markdown")
        return

    status_msg = await event.answer(f"🔍 Шукаю: **{query}**...", parse_Mode="Markdown")
    
    file_id = str(uuid.uuid4())
    song_raw = f"downloads/{file_id}"
    song_mp3 = f"downloads/{file_id}.mp3"

    try:
        search_query = f"ytsearch1:{query} audio"
        await asyncio.to_thread(download_audio_from_url, search_query, song_raw)
        
        await event.answer_audio(
            FSInputFile(song_mp3),
            caption=f"🎵 За запитом: *{query}*",
            parse_mode="Markdown"
        )
        await status_msg.delete()
    except Exception:
        await status_msg.edit_text(f"❌ Не вдалося знайти пісню за таким запитом.")
    finally:
        if os.path.exists(song_mp3):
            os.remove(song_mp3)

async def process_shazam_result(event, status_msg, out, fallback_audio=None):
    track = out.get('track')
    if not track:
        await status_msg.edit_text("😔 На жаль, не вдалося впізнати цю пісню.")
        if fallback_audio and os.path.exists(fallback_audio):
            await event.answer_audio(FSInputFile(fallback_audio), caption="Ось аудіодоріжка з відео:")
        return

    title = track.get('title', 'Невідома назва')
    subtitle = track.get('subtitle', 'Невідомий виконавець')
    full_name = f"{subtitle} - {title}"
    cover_url = track.get('images', {}).get('coverarthq')

    await status_msg.edit_text(f"✅ Знайдено: **{full_name}**\n⬇️ Завантажую повний MP3...", parse_mode="Markdown")

    song_id = str(uuid.uuid4())
    song_raw = f"downloads/{song_id}"
    song_mp3 = f"downloads/{song_id}.mp3"

    try:
        search_query = f"ytsearch1:{full_name} audio"
        await asyncio.to_thread(download_audio_from_url, search_query, song_raw)
        
        if cover_url:
            await event.answer_photo(photo=cover_url, caption=f"🎵 **{full_name}**", parse_mode="Markdown")
        
        await event.answer_audio(
            FSInputFile(song_mp3),
            title=title,
            performer=subtitle
        )
        await status_msg.delete()
    except Exception:
        await status_msg.edit_text(f"🎵 **{full_name}**\n(Не вдалося завантажити повний MP3)", parse_mode="Markdown")
    finally:
        if os.path.exists(song_mp3):
            os.remove(song_mp3)

async def main():
    print("Бот Myzonchik_ua_bot запущений і готовий до роботи!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
