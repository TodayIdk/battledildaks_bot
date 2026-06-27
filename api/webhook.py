"""
🍆 БИТВА ДИЛДАКОВ — DickGrower Style 🍆
@Battledildaks_bot
Стиль: Жёсткий 18+ Имба
"""

import os
import json
import random
import asyncio
import urllib.request
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler

import aiosqlite

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
DB_PATH = "/tmp/dickgrow.db"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ==================== TELEGRAM API ====================
def tg_request(method: str, data: dict):
    url = f"{API_URL}/{method}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"TG Error: {e}")
        return {}


def send(chat_id, text, reply_markup=None, parse_mode="HTML"):
    data = {"chat_id": chat_id, "text": text[:4000], "parse_mode": parse_mode}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return tg_request("sendMessage", data)


def edit(chat_id, msg_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "message_id": msg_id, "text": text[:4000], "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = reply_markup
    return tg_request("editMessageText", data)


def answer_cb(cb_id, text="", alert=False):
    tg_request("answerCallbackQuery", {
        "callback_query_id": cb_id,
        "text": text,
        "show_alert": alert
    })


def kb(buttons):
    return {"inline_keyboard": buttons}


# ==================== БАЗА ДАННЫХ ====================
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                dick_size REAL DEFAULT 5.0,
                last_grow TEXT,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                total_fucked INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.commit()


async def get_user(uid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (uid,)) as c:
            row = await c.fetchone()
            return dict(row) if row else None


async def create_or_update_user(uid: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, full_name, dick_size, last_grow)
            VALUES (?, ?, ?, 5.0, datetime('now', '-4 hours'))
            ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name
        """, (uid, username, full_name))
        await db.commit()


async def update_dick(uid: int, new_size: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET dick_size = ? WHERE user_id = ?", (new_size, uid))
        await db.commit()


async def update_stats(uid: int, win: bool, size_stolen: float = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        if win:
            await db.execute("""
                UPDATE users SET wins = wins + 1, total_fucked = total_fucked + 1, dick_size = dick_size + ? 
                WHERE user_id = ?
            """, (size_stolen * 0.6, uid))
        else:
            await db.execute("UPDATE users SET losses = losses + 1 WHERE user_id = ?", (uid,))
        await db.commit()


async def get_top(limit=15):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM users ORDER BY dick_size DESC LIMIT ?
        """, (limit,)) as c:
            return [dict(row) for row in await c.fetchall()]


# ==================== ИГРОВАЯ ЛОГИКА ====================
def can_grow(last_grow: str) -> bool:
    if not last_grow:
        return True
    last = datetime.fromisoformat(last_grow)
    return datetime.now() - last >= timedelta(hours=3)


def grow_dick() -> tuple[float, str]:
    base = random.uniform(1.2, 4.8)
    bonus = 0
    msg = ""

    roll = random.random()
    if roll < 0.08:   # 8% — имба
        bonus = random.uniform(6, 11)
        msg = "🔥 <b>БОЖЕСТВЕННЫЙ РОСТ!</b> Твой хуй просто ОГРОМНЫЙ!"
    elif roll < 0.25:
        bonus = random.uniform(3.5, 6)
        msg = "💥 <b>КРИТИЧЕСКИЙ РОСТ!</b> Пиздец как встал!"
    elif roll < 0.45:
        bonus = random.uniform(1.5, 3)
        msg = "😏 Нормально встал, братан."

    return round(base + bonus, 2), msg


def fight_result(attacker_size: float, defender_size: float) -> dict:
    diff = attacker_size - defender_size
    win_chance = 50 + (diff * 8)
    win_chance = max(10, min(90, win_chance))

    if random.randint(1, 100) <= win_chance:
        stolen = round(defender_size * random.uniform(0.12, 0.28), 2)
        return {"win": True, "stolen": stolen, "multiplier": 1.4}
    else:
        stolen = round(attacker_size * random.uniform(0.08, 0.18), 2)
        return {"win": False, "stolen": stolen, "multiplier": 0.6}


# ==================== ТЕКСТЫ ====================
WELCOME = """
🍆 <b>ДОБРО ПОЖАЛОВАТЬ В БИТВУ ХУЁВ!</b> 🍆

Каждые 3 часа ты можешь дрочить свой дилдак командой <b>/grow</b>
Чем больше у тебя — тем больнее ты будешь ебать других.

Начинай качать своего монстра.
"""

HELP_TEXT = """
🫡 <b>Команды бота:</b>

/grow — Вырастить свой дилдак (раз в 3 часа)
/me — Посмотреть свой хуй
/fight @username — Напасть на кого-то
/top — Топ самых огромных хуёв
"""

# ==================== КОМАНДЫ ====================
async def cmd_start(data):
    uid = data["from"]["id"]
    username = data["from"].get("username")
    full_name = data["from"].get("first_name", "") + " " + data["from"].get("last_name", "")
    chat_id = data["chat"]["id"]

    await create_or_update_user(uid, username, full_name.strip())
    send(chat_id, WELCOME, kb([[{"text": "🔥 Измерить свой хуй", "callback_data": "me"}]]))


async def cmd_grow(data):
    uid = data["from"]["id"]
    chat_id = data["chat"]["id"]
    user = await get_user(uid)

    if not user or not can_grow(user["last_grow"]):
        remaining = "через 3 часа"
        send(chat_id, f"🕒 <b>Твой хуй ещё не восстановился.</b>\n\nСледующий рост {remaining}.")
        return

    growth, special = grow_dick()
    new_size = round(user["dick_size"] + growth, 2)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET dick_size = ?, last_grow = datetime('now') WHERE user_id = ?",
            (new_size, uid)
        )
        await db.commit()

    text = f"""
🍆 <b>ТВОЙ ХУЙ ВЫРОС!</b> 🍆

{special}

📏 Новый размер: <b>{new_size} см</b>
📈 Прирост: +{growth} см
    """
    send(chat_id, text)


async def cmd_me(data):
    uid = data["from"]["id"]
    chat_id = data["chat"]["id"]
    user = await get_user(uid)

    if not user:
        send(chat_id, "Сначала напиши /start")
        return

    size = user["dick_size"]
    rank = "🪱 Червяк" if size < 10 else \
           "🥉 Норм" if size < 18 else \
           "🥈 Хороший" if size < 25 else \
           "🥇 Монстр" if size < 35 else "👑 БОГ ХУЁВ"

    text = f"""
🍆 <b>ТВОЙ ДИЛДАК</b> 🍆

📏 Размер: <b>{size} см</b>
🏆 Ранг: <b>{rank}</b>
⚔️ Побед: {user['wins']} | Поражений: {user['losses']}
💦 Всего отъебал: {user['total_fucked']} человек

<i>Чем больше — тем больнее ебешь.</i>
"""
    send(chat_id, text)


async def cmd_fight(data, target_username: str):
    attacker_id = data["from"]["id"]
    chat_id = data["chat"]["id"]

    attacker = await get_user(attacker_id)
    if not attacker:
        send(chat_id, "Напиши /start сначала.")
        return

    # Ищем цель
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE username = ? OR full_name LIKE ?",
            (target_username.strip("@"), f"%{target_username}%")
        ) as c:
            target = await c.fetchone()

    if not target:
        send(chat_id, "❌ Не нашёл такого бойца.")
        return

    target = dict(target)
    if target["user_id"] == attacker_id:
        send(chat_id, "🤡 Сам с собой хочешь подраться?")
        return

    result = fight_result(attacker["dick_size"], target["dick_size"])

    if result["win"]:
        await update_stats(attacker_id, True, result["stolen"])
        await update_dick(target["user_id"], max(3.0, target["dick_size"] - result["stolen"]))

        text = f"""
🔥 <b>ПОБЕДА!</b> 🔥

Твой хуй ({attacker['dick_size']}см) разъебал {target['full_name']} ({target['dick_size']}см)

💦 Ты отнял <b>{result['stolen']} см</b>
📏 Твой новый размер: <b>{round(attacker['dick_size'] + result['stolen']*0.6, 2)} см</b>
        """
    else:
        await update_stats(attacker_id, False)
        await update_dick(target["user_id"], target["dick_size"] + result["stolen"]*0.4)

        text = f"""
💀 <b>ТЕБЯ ОТПИЗДИЛИ</b> 💀

Хуй {target['full_name']} ({target['dick_size']}см) оказался больше и толще.

У тебя отняли <b>{result['stolen']} см</b>
Текущий размер: <b>{max(2.0, round(attacker['dick_size'] - result['stolen'], 2))} см</b>
        """

    send(chat_id, text)


async def cmd_top(chat_id):
    top = await get_top(15)
    text = "🏆 <b>ТОП САМЫХ БОЛЬШИХ ХУЁВ</b>\n\n"

    for i, user in enumerate(top, 1):
        medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"<b>{i}.</b>"
        text += f"{medal} {user['full_name']} — <b>{user['dick_size']} см</b>\n"

    send(chat_id, text)


# ==================== CALLBACKS ====================
def handle_callback(cb):
    data = cb.get("data", "")
    chat_id = cb["message"]["chat"]["id"]
    msg_id = cb["message"]["message_id"]
    uid = cb["from"]["id"]

    if data == "me":
        # Можно сделать красивую кнопку
        edit(chat_id, msg_id, "🔄 Измеряем твой хуй...", None)
        # Здесь можно добавить задержку и красивый рост, но для скорости оставим просто вызов
        import threading
        threading.Thread(target=lambda: asyncio.run(cmd_me(cb["message"]))).start()


# ==================== VERCEL HANDLER ====================
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        tg_request("setWebhook", {"url": WEBHOOK_URL, "drop_pending_updates": True})
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Webhook set successfully")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        
        try:
            update = json.loads(body)

            if "message" in update:
                msg = update["message"]
                text = msg.get("text", "")

                if text.startswith("/start"):
                    asyncio.run(cmd_start(msg))
                elif text.startswith("/grow"):
                    asyncio.run(cmd_grow(msg))
                elif text.startswith("/me") or text.startswith("/dick"):
                    asyncio.run(cmd_me(msg))
                elif text.startswith("/fight"):
                    target = text.replace("/fight", "").strip()
                    if target:
                        asyncio.run(cmd_fight(msg, target))
                elif text.startswith("/top"):
                    asyncio.run(cmd_top(msg["chat"]["id"]))
                elif text.startswith("/help"):
                    send(msg["chat"]["id"], HELP_TEXT)

            elif "callback_query" in update:
                handle_callback(update["callback_query"])

        except Exception as e:
            print("Error:", e)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
