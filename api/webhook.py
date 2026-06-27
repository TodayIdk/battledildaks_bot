"""
🍆 БИТВА ДИЛДАКОВ 🍆
@Battledildaks_bot
Vercel Serverless — БЕЗ aiogram в handler (фикс Timeout error)
Telegram Bot API через чистые HTTP запросы
"""

import os
import json
import random
import asyncio
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler

import aiosqlite

# ══════════════════════════════════════════════════════════════
# 🔧 КОНФИГ
# ══════════════════════════════════════════════════════════════

BOT_TOKEN   = os.environ.get("BOT_TOKEN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
DB_PATH     = "/tmp/dildaks.db"
API_URL     = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ══════════════════════════════════════════════════════════════
# 📡 TELEGRAM API (чистый urllib — без зависимостей)
# ══════════════════════════════════════════════════════════════

def tg_request(method: str, data: dict) -> dict:
    """Синхронный запрос к Telegram Bot API"""
    url     = f"{API_URL}/{method}"
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req     = urllib.request.Request(
        url,
        data    = payload,
        headers = {"Content-Type": "application/json; charset=utf-8"},
        method  = "POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[TG ERROR] {method}: {e}")
        return {}


def send_message(chat_id: int, text: str, reply_markup: dict = None,
                 parse_mode: str = "HTML") -> dict:
    data = {
        "chat_id":    chat_id,
        "text":       text[:4096],
        "parse_mode": parse_mode,
    }
    if reply_markup:
        data["reply_markup"] = reply_markup
    return tg_request("sendMessage", data)


def edit_message(chat_id: int, message_id: int, text: str,
                 reply_markup: dict = None, parse_mode: str = "HTML") -> dict:
    data = {
        "chat_id":    chat_id,
        "message_id": message_id,
        "text":       text[:4096],
        "parse_mode": parse_mode,
    }
    if reply_markup:
        data["reply_markup"] = reply_markup
    return tg_request("editMessageText", data)


def answer_callback(callback_id: str, text: str = "", show_alert: bool = False):
    tg_request("answerCallbackQuery", {
        "callback_query_id": callback_id,
        "text":              text[:200],
        "show_alert":        show_alert,
    })


def set_webhook_sync(url: str) -> dict:
    return tg_request("setWebhook", {
        "url":                  url,
        "drop_pending_updates": True,
        "allowed_updates":      ["message", "callback_query"],
    })


# ══════════════════════════════════════════════════════════════
# 🎨 КОНСТАНТЫ ИГРЫ
# ══════════════════════════════════════════════════════════════

RARITIES = {
    "common":    {"name": "Обычный",      "emoji": "⚪", "mult": 1.0, "chance": 45},
    "uncommon":  {"name": "Необычный",    "emoji": "🟢", "mult": 1.3, "chance": 25},
    "rare":      {"name": "Редкий",       "emoji": "🔵", "mult": 1.7, "chance": 15},
    "epic":      {"name": "Эпический",    "emoji": "🟣", "mult": 2.2, "chance": 9},
    "legendary": {"name": "Легендарный",  "emoji": "🟡", "mult": 3.0, "chance": 4},
    "mythic":    {"name": "Мифический",   "emoji": "🔴", "mult": 4.0, "chance": 1.5},
    "divine":    {"name": "Божественный", "emoji": "💠", "mult": 6.0, "chance": 0.5},
}

DILDO_NAMES = {
    "common":    ["Резиновый Новичок","Скромняга","Первый Опыт","Бюджетный Друг",
                  "Мягкий Утешитель","Силиконовый Валера","Гелевый Гена","Тихий Шалун"],
    "uncommon":  ["Вибро-Бандит","Ребристый Разбойник","Двойной Удар",
                  "Турбо-Шалун","Присоска-Мастер","Пупырчатый Карл"],
    "rare":      ["Анаконда Страсти","Титановый Терминатор","Чёрная Мамба",
                  "Королевская Кобра","Двуглавый Дракон","Бархатный Палач"],
    "epic":      ["Дилдо Хаоса","Вибро-Берсерк","Тёмный Властелин",
                  "Кристальный Разрушитель","Адская Гидра"],
    "legendary": ["Экскалибур Наслаждений","Мьёльнир Оргазмов",
                  "Жезл Посейдона","Священный Грааль","Скипетр Бездны"],
    "mythic":    ["Пожиратель Миров","Аннигилятор Целомудрия",
                  "Космический Опустошитель","Дилдо Древних Богов"],
    "divine":    ["ДИЛДО ВСЕЛЕННОЙ 🌌","АБСОЛЮТНЫЙ ОРГАЗМ ∞",
                  "БОЛЬШОЙ ВЗРЫВ 💥","СОЗДАТЕЛЬ МИРОВ 🌍"],
}

MATERIALS = [
    "силиконовый","латексный","стеклянный","металлический",
    "кристальный","ледяной","огненный","призрачный","алмазный",
    "из метеоритного железа","из тёмной материи","из лунного света",
]

ABILITIES = {
    "common":    [("Шлепок","💢",5,"шлёпает"),
                  ("Тычок","👉",7,"тычет"),
                  ("Вибрация","📳",6,"вибрирует")],
    "uncommon":  [("Двойной удар","💥",12,"бьёт дважды"),
                  ("Вихрь страсти","🌀",14,"кружит"),
                  ("Разряд","⚡",13,"бьёт током")],
    "rare":      [("Анальный торнадо","🌪",22,"закручивает"),
                  ("Оргазмический взрыв","💣",25,"взрывается"),
                  ("Пронзание","🗡",20,"пронзает")],
    "epic":      [("Цунами удовольствия","🌊",35,"накрывает волной"),
                  ("Тёмный ритуал","🔮",40,"ритуалит"),
                  ("Берсерк","😈",38,"бесится")],
    "legendary": [("Божественный оргазм","✨",55,"оргазмирует"),
                  ("Апокалипсис","☄️",60,"апокалиптит"),
                  ("Доминирование","👑",50,"доминирует")],
    "mythic":    [("Разрыв реальности","🕳",75,"рвёт реальность"),
                  ("Квантовый оргазм","⚛️",80,"квантует")],
    "divine":    [("БОЛЬШОЙ ВЗРЫВ","🌌",100,"пересоздаёт"),
                  ("∞ ЭКСТАЗ ∞","💠",120,"экстазирует")],
}

BATTLE_COMMENTS = [
    "{attacker} замахнулся «{dildo}» и {action} {defender}!",
    "«{dildo}» в руках {attacker} {action} {defender}!",
    "{attacker} крутанул «{dildo}» как вертолёт — {action} {defender}!",
    "С диким криком {attacker} обрушил «{dildo}» на {defender}!",
    "{attacker} подкрался с «{dildo}» и {action} {defender}!",
]

CRIT_COMMENTS = [
    "💥 КРИТИЧЕСКИЙ УДАР! Соседи вызвали полицию!",
    "💥 КРИТ! Сейсмологи зафиксировали толчок!",
    "💥 МОЩНЕЙШИЙ КРИТ! Даже дилдо удивился!",
]

DODGE_COMMENTS = [
    "🌀 {defender} увернулся в последний момент!",
    "🌀 {defender} сделал сальто назад! Гимнаст!",
    "🌀 Мимо! {defender} скользкий как намазанный!",
]

SHOP_ITEMS = {
    "heal_potion": {
        "name":"🧪 Смазка Исцеления",
        "desc":"Восст. 50 HP",
        "price":100, "effect":"heal", "value":50,
    },
    "mega_heal": {
        "name":"💊 Виагра Богов",
        "desc":"Полное восст. HP",
        "price":500, "effect":"full_heal", "value":0,
    },
    "atk_boost": {
        "name":"💪 Стероиды для Дилдо",
        "desc":"+15 к атаке навсегда",
        "price":800, "effect":"atk_boost", "value":15,
    },
    "crit_ring": {
        "name":"💍 Кольцо Оргазма",
        "desc":"+10% крита навсегда",
        "price":600, "effect":"crit_boost", "value":10,
    },
    "gacha_ticket": {
        "name":"🎰 Лотерейный Билет",
        "desc":"Крутануть гачу прямо сейчас",
        "price":300, "effect":"gacha", "value":0,
    },
}

QUEST_LIST = [
    {"id":"first_blood","name":"Первая кровь",  "desc":"Выиграй 1 бой",       "target":1,    "reward":200,  "type":"wins"},
    {"id":"killer",     "name":"Убийца",         "desc":"Выиграй 5 боёв",      "target":5,    "reward":500,  "type":"wins"},
    {"id":"destroyer",  "name":"Разрушитель",    "desc":"Выиграй 25 боёв",     "target":25,   "reward":2000, "type":"wins"},
    {"id":"collector",  "name":"Коллекционер",   "desc":"Собери 5 дилдаков",   "target":5,    "reward":800,  "type":"dildos"},
    {"id":"rich",       "name":"Богатенький",    "desc":"Накопи 5000 монет",   "target":5000, "reward":1000, "type":"gold"},
    {"id":"lvl10",      "name":"Десятка",        "desc":"Достигни 10 уровня",  "target":10,   "reward":1500, "type":"level"},
]

# ══════════════════════════════════════════════════════════════
# 🗄️ БАЗА ДАННЫХ (синхронная через отдельный event loop)
# ══════════════════════════════════════════════════════════════

def run(coro):
    """Запускает корутину в новом event loop — безопасно для Vercel"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                user_id          INTEGER PRIMARY KEY,
                username         TEXT    DEFAULT '',
                full_name        TEXT    DEFAULT '',
                level            INTEGER DEFAULT 1,
                exp              INTEGER DEFAULT 0,
                gold             INTEGER DEFAULT 500,
                gems             INTEGER DEFAULT 10,
                hp               INTEGER DEFAULT 100,
                max_hp           INTEGER DEFAULT 100,
                wins             INTEGER DEFAULT 0,
                losses           INTEGER DEFAULT 0,
                total_damage     INTEGER DEFAULT 0,
                arena_rating     INTEGER DEFAULT 1000,
                equipped_dildo_id INTEGER DEFAULT 0,
                last_daily       TEXT    DEFAULT '',
                last_gacha       TEXT    DEFAULT '',
                crit_bonus       INTEGER DEFAULT 0,
                atk_bonus        INTEGER DEFAULT 0,
                created_at       TEXT    DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS dildos (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id      INTEGER,
                name          TEXT,
                rarity        TEXT    DEFAULT 'common',
                material      TEXT    DEFAULT '',
                level         INTEGER DEFAULT 1,
                exp           INTEGER DEFAULT 0,
                base_atk      INTEGER DEFAULT 10,
                base_def      INTEGER DEFAULT 5,
                base_spd      INTEGER DEFAULT 5,
                hp            INTEGER DEFAULT 50,
                max_hp        INTEGER DEFAULT 50,
                crit_chance   INTEGER DEFAULT 5,
                ability_name  TEXT    DEFAULT '',
                ability_emoji TEXT    DEFAULT '',
                ability_dmg   INTEGER DEFAULT 5,
                ability_desc  TEXT    DEFAULT '',
                kills         INTEGER DEFAULT 0,
                created_at    TEXT    DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS inventory (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id  INTEGER,
                item_id  TEXT,
                quantity INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS quest_progress (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER,
                quest_id  TEXT,
                progress  INTEGER DEFAULT 0,
                claimed   INTEGER DEFAULT 0
            );
        """)
        await db.commit()


async def _get_player(uid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM players WHERE user_id=?", (uid,)
        ) as c:
            row = await c.fetchone()
            return dict(row) if row else None


async def _create_player(uid: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO players (user_id,username,full_name) VALUES (?,?,?)",
            (uid, username, full_name)
        )
        await db.commit()


async def _update_player(uid: int, **kw):
    if not kw:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        sets = ", ".join(f"{k}=?" for k in kw)
        vals = list(kw.values()) + [uid]
        await db.execute(f"UPDATE players SET {sets} WHERE user_id=?", vals)
        await db.commit()


async def _get_dildos(uid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM dildos WHERE owner_id=? ORDER BY base_atk DESC", (uid,)
        ) as c:
            rows = await c.fetchall()
            return [dict(r) for r in rows]


async def _get_dildo(did: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM dildos WHERE id=?", (did,)
        ) as c:
            row = await c.fetchone()
            return dict(row) if row else None


async def _create_dildo(owner_id: int, rarity: str = None) -> dict:
    if not rarity:
        rarity = _roll_rarity()
    r    = RARITIES[rarity]
    name = random.choice(DILDO_NAMES[rarity])
    mat  = random.choice(MATERIALS)
    ab   = random.choice(ABILITIES[rarity])
    atk  = int(random.randint(8,15)  * r["mult"])
    dfn  = int(random.randint(3,10)  * r["mult"])
    spd  = int(random.randint(3,10)  * r["mult"])
    hp   = int(random.randint(40,70) * r["mult"])
    crit = 5 + int(r["mult"] * 2)

    async with aiosqlite.connect(DB_PATH) as db:
        c = await db.execute(
            """INSERT INTO dildos
            (owner_id,name,rarity,material,base_atk,base_def,base_spd,
             hp,max_hp,crit_chance,ability_name,ability_emoji,ability_dmg,ability_desc)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (owner_id,name,rarity,mat,atk,dfn,spd,hp,hp,crit,
             ab[0],ab[1],ab[2],ab[3])
        )
        did = c.lastrowid
        await db.commit()

    return {
        "id":did,"name":name,"rarity":rarity,"material":mat,
        "base_atk":atk,"base_def":dfn,"base_spd":spd,
        "hp":hp,"max_hp":hp,"crit_chance":crit,
        "ability_name":ab[0],"ability_emoji":ab[1],
        "ability_dmg":ab[2],"ability_desc":ab[3],
    }


async def _add_item(uid: int, item_id: str, qty: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id,quantity FROM inventory WHERE user_id=? AND item_id=?",
            (uid, item_id)
        ) as c:
            row = await c.fetchone()
        if row:
            await db.execute(
                "UPDATE inventory SET quantity=quantity+? WHERE id=?", (qty, row[0])
            )
        else:
            await db.execute(
                "INSERT INTO inventory (user_id,item_id,quantity) VALUES (?,?,?)",
                (uid, item_id, qty)
            )
        await db.commit()


async def _use_item(uid: int, item_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id,quantity FROM inventory WHERE user_id=? AND item_id=?",
            (uid, item_id)
        ) as c:
            row = await c.fetchone()
        if row and row[1] > 0:
            await db.execute(
                "UPDATE inventory SET quantity=quantity-1 WHERE id=?", (row[0],)
            )
            await db.commit()
            return True
        return False


async def _get_inventory(uid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM inventory WHERE user_id=? AND quantity>0", (uid,)
        ) as c:
            rows = await c.fetchall()
            return [dict(r) for r in rows]


async def _get_quest(uid: int, qid: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM quest_progress WHERE user_id=? AND quest_id=?",
            (uid, qid)
        ) as c:
            row = await c.fetchone()
            return dict(row) if row else None


async def _upsert_quest(uid: int, qid: str, progress: int):
    async with aiosqlite.connect(DB_PATH) as db:
        row = await _get_quest(uid, qid)
        if row:
            await db.execute(
                "UPDATE quest_progress SET progress=? WHERE user_id=? AND quest_id=?",
                (progress, uid, qid)
            )
        else:
            await db.execute(
                "INSERT INTO quest_progress (user_id,quest_id,progress) VALUES (?,?,?)",
                (uid, qid, progress)
            )
        await db.commit()


async def _claim_quest_db(uid: int, qid: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE quest_progress SET claimed=1 WHERE user_id=? AND quest_id=?",
            (uid, qid)
        )
        await db.commit()


async def _get_top(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM players ORDER BY arena_rating DESC LIMIT ?", (limit,)
        ) as c:
            rows = await c.fetchall()
            return [dict(r) for r in rows]


async def _count(table: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(f"SELECT COUNT(*) FROM {table}") as c:
            row = await c.fetchone()
            return row[0]


async def _add_exp(uid: int, amount: int):
    p     = await _get_player(uid)
    exp   = p["exp"] + amount
    level = p["level"]
    up    = False
    while exp >= _exp_need(level):
        exp  -= _exp_need(level)
        level += 1
        up    = True
    hp = 100 + (level-1)*15
    await _update_player(uid, exp=exp, level=level, max_hp=hp, hp=hp)
    return up, level


async def _add_dildo_exp(did: int, amount: int):
    d = await _get_dildo(did)
    if not d:
        return False, 0
    exp   = d["exp"] + amount
    level = d["level"]
    up    = False
    while exp >= _dildo_exp_need(level):
        exp  -= _dildo_exp_need(level)
        level += 1
        up    = True
    r   = RARITIES[d["rarity"]]
    lvl_diff = level - d["level"]
    atk = d["base_atk"] + int(2*r["mult"]) * lvl_diff
    dfn = d["base_def"] + int(1*r["mult"]) * lvl_diff
    hp  = d["max_hp"]  + int(5*r["mult"]) * lvl_diff
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE dildos SET exp=?,level=?,base_atk=?,base_def=?,hp=?,max_hp=? WHERE id=?",
            (exp,level,atk,dfn,hp,hp,did)
        )
        await db.commit()
    return up, level


async def _dildo_kill(did: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE dildos SET kills=kills+1 WHERE id=?", (did,)
        )
        await db.commit()


# ══════════════════════════════════════════════════════════════
# 🎲 ИГРОВАЯ ЛОГИКА (синхронная)
# ══════════════════════════════════════════════════════════════

def _roll_rarity() -> str:
    roll = random.uniform(0, 100)
    cum  = 0
    for rar, data in RARITIES.items():
        cum += data["chance"]
        if roll <= cum:
            return rar
    return "common"


def _exp_need(lvl: int) -> int:
    return int(100 * (lvl ** 1.5))


def _dildo_exp_need(lvl: int) -> int:
    return int(50 * (lvl ** 1.3))


def _exp_bar(cur: int, need: int, size: int = 10) -> str:
    filled = int((cur / max(1, need)) * size)
    return "█" * filled + "░" * (size - filled)


def _rank(rating: int) -> str:
    if rating >= 2000: return "💎 Алмаз"
    if rating >= 1600: return "🥇 Золото"
    if rating >= 1300: return "🥈 Серебро"
    if rating >= 1000: return "🥉 Бронза"
    return "🪵 Дерево"


def _gen_enemy(player_level: int) -> dict:
    level  = max(1, player_level + random.randint(-2, 3))
    rarity = _roll_rarity()
    r      = RARITIES[rarity]
    names  = [
        "Безумный Вибратор","Дикий Фаллос","Резиновый Бандит",
        "Силиконовый Маньяк","Призрачный Хер","Демон Наслаждений",
        "Гоблин-Извращенец","Тролль с Дилдаком","Орк-Доминатор",
        "Суккуб Подворотни","Скелет-Онанист","Дракон-Нимфоман",
    ]
    ab = random.choice(ABILITIES[rarity])
    return {
        "name":         random.choice(names),
        "level":        level,
        "rarity":       rarity,
        "dildo_name":   random.choice(DILDO_NAMES[rarity]),
        "atk":          int((8  + level*3)  * r["mult"]),
        "defense":      int((3  + level*2)  * r["mult"]),
        "hp":           int((40 + level*12) * r["mult"]),
        "crit":         5 + int(r["mult"]*2),
        "ability_name": ab[0], "ability_emoji": ab[1],
        "ability_dmg":  ab[2], "ability_desc":  ab[3],
    }


async def _simulate_battle(uid: int, did: int, enemy: dict) -> dict:
    """Полная симуляция боя"""
    player = await _get_player(uid)
    dildo  = await _get_dildo(did)
    if not dildo:
        return {"error": "Нет дилдо!"}

    p_name = player["full_name"] or player["username"] or "Воин"
    e_name = enemy["name"]

    p_hp   = dildo["max_hp"]
    e_hp   = enemy["hp"]
    p_atk  = dildo["base_atk"] + player["atk_bonus"]
    p_def  = dildo["base_def"]
    p_crit = dildo["crit_chance"] + player["crit_bonus"]
    e_atk  = enemy["atk"]
    e_def  = enemy["defense"]
    e_crit = enemy["crit"]

    log   = []
    rnd   = 0
    p_dmg = 0

    log.append(f"⚔️ <b>{p_name}</b> VS <b>{e_name}</b> (Ур.{enemy['level']})")
    log.append(f"🍆 «{dildo['name']}» VS «{enemy['dildo_name']}»")
    log.append(f"❤️ {p_hp} HP | ❤️ {e_hp} HP")
    log.append("━"*26)

    while p_hp > 0 and e_hp > 0 and rnd < 15:
        rnd += 1
        log.append(f"\n📍 <b>Раунд {rnd}</b>")

        # Ход игрока
        use_ab = random.random() < 0.3 and rnd > 1
        raw    = (dildo["ability_dmg"] + int(p_atk*0.5)) if use_ab \
                 else p_atk + random.randint(-3, 5)
        act    = (f"{dildo['ability_emoji']} <b>{dildo['ability_name']}</b>!") if use_ab \
                 else random.choice(BATTLE_COMMENTS).format(
                     attacker=p_name, defender=e_name,
                     dildo=dildo["name"], action=dildo["ability_desc"]
                 )
        is_crit  = random.randint(1,100) <= p_crit
        is_dodge = random.randint(1,100) <= min(25, e_def//2)
        if is_crit: raw = int(raw * 1.8)

        if is_dodge:
            log.append(random.choice(DODGE_COMMENTS).format(
                defender=e_name, dildo=dildo["name"]
            ))
        else:
            dmg   = max(1, raw - e_def//3)
            e_hp -= dmg
            p_dmg += dmg
            log.append(f"  {act}")
            if is_crit:
                log.append(f"  {random.choice(CRIT_COMMENTS)}")
            log.append(f"  💔 -{dmg} HP | {e_name}: {max(0,e_hp)} HP")

        if e_hp <= 0:
            break

        # Ход врага
        use_ab_e  = random.random() < 0.25
        raw_e     = (enemy["ability_dmg"] + int(e_atk*0.5)) if use_ab_e \
                    else e_atk + random.randint(-3, 5)
        act_e     = (f"{enemy['ability_emoji']} <b>{enemy['ability_name']}</b>!") if use_ab_e \
                    else random.choice(BATTLE_COMMENTS).format(
                        attacker=e_name, defender=p_name,
                        dildo=enemy["dildo_name"], action=enemy["ability_desc"]
                    )
        is_crit_e  = random.randint(1,100) <= e_crit
        is_dodge_e = random.randint(1,100) <= min(25, p_def//2)
        if is_crit_e: raw_e = int(raw_e * 1.8)

        if is_dodge_e:
            log.append(random.choice(DODGE_COMMENTS).format(
                defender=p_name, dildo=enemy["dildo_name"]
            ))
        else:
            dmg_e  = max(1, raw_e - p_def//3)
            p_hp  -= dmg_e
            log.append(f"  {act_e}")
            if is_crit_e:
                log.append(f"  {random.choice(CRIT_COMMENTS)}")
            log.append(f"  💔 -{dmg_e} HP | {p_name}: {max(0,p_hp)} HP")

    log.append("\n" + "═"*26)
    won  = p_hp > 0
    gold = int(30  * enemy["level"] * RARITIES[enemy["rarity"]]["mult"])
    xp   = int(25  * enemy["level"] * RARITIES[enemy["rarity"]]["mult"])
    dxp  = int(15  * enemy["level"] * RARITIES[enemy["rarity"]]["mult"])

    if won:
        log.append(f"🏆 <b>ПОБЕДА!</b> {p_name} уничтожил {e_name}!")
        log.append(f"💰 +{gold} золота | ⭐ +{xp} опыта | 💥 Урон: {p_dmg}")

        p2 = await _get_player(uid)
        await _update_player(uid,
            gold=p2["gold"]+gold,
            wins=p2["wins"]+1,
            total_damage=p2["total_damage"]+p_dmg,
        )
        up, lvl = await _add_exp(uid, xp)
        if up:
            log.append(f"🎉 <b>УРОВЕНЬ {lvl}!</b>")

        dup, dlvl = await _add_dildo_exp(did, dxp)
        if dup:
            log.append(f"🍆✨ Дилдо вырос до {dlvl} уровня!")

        await _dildo_kill(did)

        # Дроп
        if random.randint(1,100) <= 15 + int(RARITIES[enemy["rarity"]]["mult"]*5):
            drop = await _create_dildo(uid, enemy["rarity"])
            rr   = RARITIES[drop["rarity"]]
            log.append(f"\n🎁 <b>ДРОП!</b> {rr['emoji']} «{drop['name']}» [{rr['name']}]")
            log.append(f"  ⚔️{drop['base_atk']} 🛡{drop['base_def']} ❤️{drop['hp']}")

        # Квесты
        p3 = await _get_player(uid)
        await _upsert_quest(uid, "first_blood", p3["wins"])
        await _upsert_quest(uid, "killer",      p3["wins"])
        await _upsert_quest(uid, "destroyer",   p3["wins"])
    else:
        log.append(f"💀 <b>ПОРАЖЕНИЕ!</b> Возвращайся сильнее!")
        log.append(f"⭐ +{int(xp*0.3)} опыта | 💥 Урон: {p_dmg}")
        p2 = await _get_player(uid)
        await _update_player(uid,
            losses=p2["losses"]+1,
            total_damage=p2["total_damage"]+p_dmg,
        )
        await _add_exp(uid, int(xp*0.3))

    return {"won": won, "log": "\n".join(log)}


# ══════════════════════════════════════════════════════════════
# ⌨️ КЛАВИАТУРЫ (dict для urllib)
# ══════════════════════════════════════════════════════════════

def kb_main() -> dict:
    return {"inline_keyboard": [
        [{"text":"👤 Профиль",   "callback_data":"profile"},
         {"text":"🍆 Коллекция","callback_data":"collection"}],
        [{"text":"⚔️ В БОЙ!",   "callback_data":"battle"},
         {"text":"🏟 Арена",    "callback_data":"arena"}],
        [{"text":"🎰 Гача",      "callback_data":"gacha"},
         {"text":"🎁 Ежедневка","callback_data":"daily"}],
        [{"text":"🛒 Магазин",   "callback_data":"shop"},
         {"text":"🎒 Инвентарь","callback_data":"inventory"}],
        [{"text":"📜 Квесты",    "callback_data":"quests"},
         {"text":"🏆 Топ",       "callback_data":"top"}],
    ]}


def kb_back() -> dict:
    return {"inline_keyboard": [
        [{"text":"🔙 Меню","callback_data":"menu"}]
    ]}


def kb_after_battle() -> dict:
    return {"inline_keyboard": [
        [{"text":"⚔️ Ещё бой!","callback_data":"battle"},
         {"text":"🔙 Меню",    "callback_data":"menu"}],
    ]}


def kb_collection(dildos: list, page: int = 0) -> dict:
    per  = 5
    sl   = dildos[page*per : page*per+per]
    rows = []
    for d in sl:
        r = RARITIES[d["rarity"]]
        rows.append([{"text": f"{r['emoji']} {d['name']} Ур.{d['level']} ⚔️{d['base_atk']}",
                      "callback_data": f"dildo_{d['id']}"}])
    nav = []
    if page > 0:
        nav.append({"text":"⬅️","callback_data":f"colp_{page-1}"})
    if (page+1)*per < len(dildos):
        nav.append({"text":"➡️","callback_data":f"colp_{page+1}"})
    if nav:
        rows.append(nav)
    rows.append([{"text":"🔙 Меню","callback_data":"menu"}])
    return {"inline_keyboard": rows}


def kb_dildo(did: int, equipped: bool) -> dict:
    rows = []
    if not equipped:
        rows.append([{"text":"⚔️ Экипировать","callback_data":f"equip_{did}"}])
    rows.append([{"text":"🔙 Коллекция","callback_data":"collection"}])
    return {"inline_keyboard": rows}


def kb_shop() -> dict:
    rows = [
        [{"text": f"{i['name']} — 💰{i['price']}", "callback_data": f"buy_{k}"}]
        for k, i in SHOP_ITEMS.items()
    ]
    rows.append([{"text":"🔙 Меню","callback_data":"menu"}])
    return {"inline_keyboard": rows}


def kb_inv(items: list) -> dict:
    rows = []
    for item in items:
        si = SHOP_ITEMS.get(item["item_id"])
        if si:
            rows.append([{"text": f"Использовать {si['name']}",
                          "callback_data": f"use_{item['item_id']}"}])
    rows.append([{"text":"🔙 Меню","callback_data":"menu"}])
    return {"inline_keyboard": rows}


def kb_quests(quest_buttons: list) -> dict:
    rows = [[{"text": f"🎁 Забрать: {name}", "callback_data": f"claim_{qid}"}]
            for qid, name in quest_buttons]
    rows.append([{"text":"🔙 Меню","callback_data":"menu"}])
    return {"inline_keyboard": rows}


# ══════════════════════════════════════════════════════════════
# 🎮 ОБРАБОТЧИКИ (всё синхронно через run())
# ══════════════════════════════════════════════════════════════

def handle_start(uid: int, username: str, full_name: str, chat_id: int):
    run(_init_db())
    player = run(_get_player(uid))

    if not player:
        run(_create_player(uid, username, full_name))
        d = run(_create_dildo(uid, "common"))

        async def _set_equip():
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute(
                    "UPDATE players SET equipped_dildo_id=? WHERE user_id=?",
                    (d["id"], uid)
                )
                await db.commit()
        run(_set_equip())

        for q in QUEST_LIST:
            run(_upsert_quest(uid, q["id"], 0))

        r    = RARITIES[d["rarity"]]
        text = (
            "🍆💥 <b>ДОБРО ПОЖАЛОВАТЬ В БИТВУ ДИЛДАКОВ!</b> 💥🍆\n\n"
            "Мир, где резиновые воины сражаются за честь!\n\n"
            f"🎁 <b>Твой первый дилдак:</b>\n"
            f"{r['emoji']} <b>«{d['name']}»</b> [{r['name']}]\n"
            f"🔨 {d['material']}\n"
            f"⚔️{d['base_atk']} 🛡{d['base_def']} 💨{d['base_spd']} ❤️{d['hp']}\n"
            f"✨ {d['ability_emoji']} {d['ability_name']}\n\n"
            "<i>Вперёд к победам, воин!</i> 🍆⚔️"
        )
    else:
        run(_update_player(uid, username=username, full_name=full_name))
        text = f"🍆 С возвращением, <b>{full_name or username}</b>!\n\nГотов к битвам?"

    send_message(chat_id, text, kb_main())


def handle_profile(uid: int, chat_id: int, message_id: int = None, cb_id: str = None):
    run(_init_db())
    p = run(_get_player(uid))
    if not p:
        send_message(chat_id, "❌ Сначала /start!")
        return

    dildos = run(_get_dildos(uid))
    dildo  = run(_get_dildo(p["equipped_dildo_id"])) if p["equipped_dildo_id"] else None
    total  = p["wins"] + p["losses"]
    wr     = p["wins"] / max(1, total) * 100
    need   = _exp_need(p["level"])

    text = (
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"🏷 {p['full_name'] or p['username'] or 'Аноним'}\n"
        f"📊 Уровень: <b>{p['level']}</b>\n"
        f"📈 [{_exp_bar(p['exp'],need)}] {p['exp']}/{need}\n\n"
        f"💰 {p['gold']} | 💎 {p['gems']}\n\n"
        f"⚔️ Побед: <b>{p['wins']}</b> | 💀 Поражений: <b>{p['losses']}</b>\n"
        f"📊 Винрейт: <b>{wr:.1f}%</b> | 💥 Урон: <b>{p['total_damage']}</b>\n\n"
        f"🏟 Рейтинг: <b>{p['arena_rating']}</b> {_rank(p['arena_rating'])}\n"
        f"🍆 Дилдаков: <b>{len(dildos)}</b>\n"
    )
    if dildo:
        r = RARITIES[dildo["rarity"]]
        text += (
            f"\n🗡 <b>Экипировано:</b>\n"
            f"  {r['emoji']} «{dildo['name']}» Ур.{dildo['level']}\n"
            f"  ⚔️{dildo['base_atk']} 🛡{dildo['base_def']} ❤️{dildo['hp']}"
        )
    else:
        text += "\n⚠️ Нет экипированного дилдо!"

    if message_id:
        edit_message(chat_id, message_id, text, kb_back())
    else:
        send_message(chat_id, text, kb_back())
    if cb_id:
        answer_callback(cb_id)


def handle_collection(uid: int, chat_id: int, message_id: int = None,
                      cb_id: str = None, page: int = 0):
    run(_init_db())
    dildos = run(_get_dildos(uid))
    if not dildos:
        txt = "😔 Коллекция пуста. Нажми /start"
        if message_id:
            edit_message(chat_id, message_id, txt, kb_back())
        else:
            send_message(chat_id, txt, kb_back())
        if cb_id: answer_callback(cb_id)
        return

    txt = f"🍆 <b>КОЛЛЕКЦИЯ</b> — {len(dildos)} шт.\nНажми на дилдак:"
    if message_id:
        edit_message(chat_id, message_id, txt, kb_collection(dildos, page))
    else:
        send_message(chat_id, txt, kb_collection(dildos, page))
    if cb_id: answer_callback(cb_id)


def handle_dildo_detail(uid: int, chat_id: int, message_id: int,
                        cb_id: str, did: int):
    run(_init_db())
    dildo  = run(_get_dildo(did))
    if not dildo:
        answer_callback(cb_id, "Дилдо не найден!", True)
        return
    player = run(_get_player(uid))
    r      = RARITIES[dildo["rarity"]]
    eq     = player["equipped_dildo_id"] == did
    need   = _dildo_exp_need(dildo["level"])

    text = (
        f"{r['emoji']} <b>«{dildo['name']}»</b>"
        f"{' ⚔️ ЭКИПИРОВАН' if eq else ''}\n\n"
        f"📦 {r['name']} {r['emoji']}\n"
        f"🔨 {dildo['material']}\n"
        f"📊 Уровень {dildo['level']} | "
        f"[{_exp_bar(dildo['exp'],need,10)}] {dildo['exp']}/{need}\n\n"
        f"⚔️ ATK: <b>{dildo['base_atk']}</b>\n"
        f"🛡 DEF: <b>{dildo['base_def']}</b>\n"
        f"💨 SPD: <b>{dildo['base_spd']}</b>\n"
        f"❤️ HP: <b>{dildo['hp']}/{dildo['max_hp']}</b>\n"
        f"🎯 Крит: <b>{dildo['crit_chance']}%</b>\n\n"
        f"✨ {dildo['ability_emoji']} <b>{dildo['ability_name']}</b>\n"
        f"   <i>{dildo['ability_desc']}</i> (💥{dildo['ability_dmg']})\n\n"
        f"💀 Убийств: {dildo['kills']}"
    )
    edit_message(chat_id, message_id, text, kb_dildo(did, eq))
    answer_callback(cb_id)


def handle_equip(uid: int, chat_id: int, message_id: int, cb_id: str, did: int):
    run(_init_db())
    dildo = run(_get_dildo(did))
    if not dildo or dildo["owner_id"] != uid:
        answer_callback(cb_id, "❌ Не твой дилдо!", True)
        return
    run(_update_player(uid, equipped_dildo_id=did))
    r = RARITIES[dildo["rarity"]]
    answer_callback(cb_id, f"✅ Экипирован: {r['emoji']} «{dildo['name']}»!", True)
    handle_dildo_detail(uid, chat_id, message_id, cb_id="", did=did)


def handle_battle(uid: int, chat_id: int, message_id: int = None,
                  cb_id: str = None, arena: bool = False):
    run(_init_db())
    p = run(_get_player(uid))
    if not p:
        send_message(chat_id, "❌ Сначала /start!")
        return
    if not p["equipped_dildo_id"]:
        txt = "⚠️ Нет экипированного дилдо!\n/collection → выбери и экипируй."
        send_message(chat_id, txt, kb_back())
        if cb_id: answer_callback(cb_id)
        return

    enemy = _gen_enemy(p["level"])
    r     = RARITIES[enemy["rarity"]]
    intro = (
        f"⚔️💥 <b>{'АРЕНА' if arena else 'БОЙ'}!</b>\n\n"
        f"VS <b>{enemy['name']}</b> (Ур.{enemy['level']})\n"
        f"{r['emoji']} «{enemy['dildo_name']}» [{r['name']}]\n"
        f"⚔️{enemy['atk']} 🛡{enemy['defense']} ❤️{enemy['hp']}\n\n"
        f"<i>Бой идёт...</i> 🔄"
    )
    send_message(chat_id, intro)
    if cb_id: answer_callback(cb_id)

    result = run(_simulate_battle(uid, p["equipped_dildo_id"], enemy))

    if "error" in result:
        send_message(chat_id, f"❌ {result['error']}", kb_back())
        return

    if arena:
        p2 = run(_get_player(uid))
        if result["won"]:
            ch = random.randint(15, 35)
            run(_update_player(uid, arena_rating=p2["arena_rating"]+ch))
            result["log"] += f"\n🏟 Рейтинг: +{ch} → {p2['arena_rating']+ch}"
        else:
            ch = random.randint(10, 25)
            nr = max(0, p2["arena_rating"]-ch)
            run(_update_player(uid, arena_rating=nr))
            result["log"] += f"\n🏟 Рейтинг: -{ch} → {nr}"

    log = result["log"]
    if len(log) > 4000:
        log = log[:3900] + "\n\n...(слишком эпичный бой!)"

    send_message(chat_id, log, kb_after_battle())


def handle_gacha(uid: int, chat_id: int, message_id: int = None, cb_id: str = None):
    run(_init_db())
    p = run(_get_player(uid))
    if not p:
        send_message(chat_id, "❌ /start")
        return

    now = datetime.now()
    if p["last_gacha"]:
        diff = now - datetime.fromisoformat(p["last_gacha"])
        if diff < timedelta(hours=4):
            rem  = timedelta(hours=4) - diff
            h, m = rem.seconds//3600, (rem.seconds%3600)//60
            txt  = f"⏳ Гача через <b>{h}ч {m}мин</b>\n\nКупи 🎰 Билет в /shop"
            if message_id:
                edit_message(chat_id, message_id, txt, kb_back())
            else:
                send_message(chat_id, txt, kb_back())
            if cb_id: answer_callback(cb_id)
            return

    run(_update_player(uid, last_gacha=now.isoformat()))
    d = run(_create_dildo(uid))
    r = RARITIES[d["rarity"]]

    effects = {
        "common":    "Ну... бывает.",
        "uncommon":  "Неплохо!",
        "rare":      "О, интересно! 👀",
        "epic":      "ЭПИК! 🔥",
        "legendary": "ЛЕГЕНДАРКА! 🌟🌟🌟",
        "mythic":    "МИФИЧЕСКИЙ?! ТЫ ИЗБРАННЫЙ! ⚡",
        "divine":    "Б О Ж Е С Т В Е Н Н Ы Й. Ты выиграл. 💠",
    }
    text = (
        f"🎰 <b>ГАЧА!</b>\n\n"
        f"{r['emoji']} <b>«{d['name']}»</b> [{r['name']}]\n"
        f"🔨 {d['material']}\n"
        f"⚔️{d['base_atk']} 🛡{d['base_def']} 💨{d['base_spd']} ❤️{d['hp']}\n"
        f"✨ {d['ability_emoji']} {d['ability_name']}\n\n"
        f"<i>{effects[d['rarity']]}</i>\n\n"
        f"⏳ Следующая гача через 4 часа"
    )
    dildos = run(_get_dildos(uid))
    run(_upsert_quest(uid, "collector", len(dildos)))

    if message_id:
        edit_message(chat_id, message_id, text, kb_back())
    else:
        send_message(chat_id, text, kb_back())
    if cb_id: answer_callback(cb_id)


def handle_daily(uid: int, chat_id: int, message_id: int = None, cb_id: str = None):
    run(_init_db())
    p   = run(_get_player(uid))
    if not p:
        send_message(chat_id, "❌ /start")
        return
    now = datetime.now().date().isoformat()
    if p["last_daily"] == now:
        txt = "⏳ Ежедневка уже получена! Приходи завтра 🌅"
        if message_id:
            edit_message(chat_id, message_id, txt, kb_back())
        else:
            send_message(chat_id, txt, kb_back())
        if cb_id: answer_callback(cb_id)
        return

    gold = random.randint(100,300) + p["level"]*20
    gems = random.randint(1,5)
    xp   = random.randint(30,80)  + p["level"]*10

    run(_update_player(uid, last_daily=now,
                       gold=p["gold"]+gold, gems=p["gems"]+gems))
    up, lvl = run(_add_exp(uid, xp))

    text = (
        f"🎁 <b>ЕЖЕДНЕВНАЯ НАГРАДА!</b>\n\n"
        f"💰 +{gold} золота\n💎 +{gems} гемов\n⭐ +{xp} опыта\n"
    )
    if up:
        text += f"\n🎉 <b>УРОВЕНЬ {lvl}!</b>"
    if random.random() < 0.10:
        dd  = run(_create_dildo(uid))
        rr  = RARITIES[dd["rarity"]]
        text += f"\n\n🎊 <b>БОНУС!</b> {rr['emoji']} «{dd['name']}» [{rr['name']}]"
    text += "\n\n<i>Приходи завтра!</i>"

    if message_id:
        edit_message(chat_id, message_id, text, kb_back())
    else:
        send_message(chat_id, text, kb_back())
    if cb_id: answer_callback(cb_id)


def handle_shop(uid: int, chat_id: int, message_id: int = None, cb_id: str = None):
    run(_init_db())
    p = run(_get_player(uid))
    if not p:
        send_message(chat_id, "❌ /start")
        return
    text = f"🛒 <b>МАГАЗИН</b>\n\n💰 {p['gold']} | 💎 {p['gems']}\n\n"
    for item in SHOP_ITEMS.values():
        text += f"{item['name']}\n  <i>{item['desc']}</i>\n\n"
    if message_id:
        edit_message(chat_id, message_id, text, kb_shop())
    else:
        send_message(chat_id, text, kb_shop())
    if cb_id: answer_callback(cb_id)


def handle_buy(uid: int, chat_id: int, message_id: int,
               cb_id: str, item_id: str):
    run(_init_db())
    if item_id not in SHOP_ITEMS:
        answer_callback(cb_id, "❌ Товар не найден!", True)
        return
    p    = run(_get_player(uid))
    item = SHOP_ITEMS[item_id]
    if p["gold"] < item["price"]:
        answer_callback(cb_id, f"❌ Нужно {item['price']}💰, у тебя {p['gold']}", True)
        return

    run(_update_player(uid, gold=p["gold"]-item["price"]))

    if item["effect"] == "gacha":
        d = run(_create_dildo(uid))
        r = RARITIES[d["rarity"]]
        answer_callback(cb_id, f"🎰 {r['emoji']} «{d['name']}»!", True)
    elif item["effect"] == "heal":
        p2 = run(_get_player(uid))
        run(_update_player(uid, hp=min(p2["max_hp"], p2["hp"]+item["value"])))
        answer_callback(cb_id, f"💚 +{item['value']} HP!", True)
    elif item["effect"] == "full_heal":
        p2 = run(_get_player(uid))
        run(_update_player(uid, hp=p2["max_hp"]))
        answer_callback(cb_id, "💚 HP полностью восстановлено!", True)
    elif item["effect"] == "atk_boost":
        p2 = run(_get_player(uid))
        run(_update_player(uid, atk_bonus=p2["atk_bonus"]+item["value"]))
        answer_callback(cb_id, f"💪 +{item['value']} ATK навсегда!", True)
    elif item["effect"] == "crit_boost":
        p2 = run(_get_player(uid))
        run(_update_player(uid, crit_bonus=p2["crit_bonus"]+item["value"]))
        answer_callback(cb_id, f"🎯 +{item['value']}% крита!", True)
    else:
        run(_add_item(uid, item_id))
        answer_callback(cb_id, f"✅ {item['name']} куплено!", True)

    handle_shop(uid, chat_id, message_id)


def handle_inventory(uid: int, chat_id: int, message_id: int = None, cb_id: str = None):
    run(_init_db())
    items = run(_get_inventory(uid))
    if not items:
        txt = "🎒 Инвентарь пуст! Загляни в /shop"
        if message_id:
            edit_message(chat_id, message_id, txt, kb_back())
        else:
            send_message(chat_id, txt, kb_back())
        if cb_id: answer_callback(cb_id)
        return
    text = "🎒 <b>ИНВЕНТАРЬ</b>\n\n"
    for item in items:
        si = SHOP_ITEMS.get(item["item_id"])
        if si:
            text += f"{si['name']} x{item['quantity']}\n  <i>{si['desc']}</i>\n\n"
    if message_id:
        edit_message(chat_id, message_id, text, kb_inv(items))
    else:
        send_message(chat_id, text, kb_inv(items))
    if cb_id: answer_callback(cb_id)


def handle_use(uid: int, chat_id: int, message_id: int, cb_id: str, item_id: str):
    run(_init_db())
    ok = run(_use_item(uid, item_id))
    if not ok:
        answer_callback(cb_id, "❌ Нет предмета!", True)
        return
    item = SHOP_ITEMS.get(item_id)
    if not item:
        return
    p = run(_get_player(uid))
    if item["effect"] == "heal":
        new_hp = min(p["max_hp"], p["hp"]+item["value"])
        run(_update_player(uid, hp=new_hp))
        answer_callback(cb_id, f"💚 +{item['value']} HP → {new_hp}/{p['max_hp']}", True)
    elif item["effect"] == "full_heal":
        run(_update_player(uid, hp=p["max_hp"]))
        answer_callback(cb_id, "💚 HP полностью!", True)
    handle_inventory(uid, chat_id, message_id)


def handle_quests(uid: int, chat_id: int, message_id: int = None, cb_id: str = None):
    run(_init_db())
    text    = "📜 <b>КВЕСТЫ</b>\n\n"
    claimable = []
    for q in QUEST_LIST:
        pr   = run(_get_quest(uid, q["id"]))
        cur  = pr["progress"] if pr else 0
        cl   = bool(pr["claimed"]) if pr else False
        done = cur >= q["target"]
        icon = "✅" if cl else ("🎁" if done else "🔄")
        bar  = _exp_bar(cur, q["target"], 8)
        text += (
            f"{icon} <b>{q['name']}</b>\n"
            f"   {q['desc']}\n"
            f"   [{bar}] {cur}/{q['target']} | 💰{q['reward']}\n\n"
        )
        if done and not cl:
            claimable.append((q["id"], q["name"]))

    if message_id:
        edit_message(chat_id, message_id, text, kb_quests(claimable))
    else:
        send_message(chat_id, text, kb_quests(claimable))
    if cb_id: answer_callback(cb_id)


def handle_claim(uid: int, chat_id: int, message_id: int, cb_id: str, qid: str):
    run(_init_db())
    q  = next((x for x in QUEST_LIST if x["id"]==qid), None)
    if not q:
        answer_callback(cb_id, "Квест не найден!", True)
        return
    pr = run(_get_quest(uid, qid))
    if not pr or pr["progress"] < q["target"]:
        answer_callback(cb_id, "Квест не выполнен!", True)
        return
    if pr["claimed"]:
        answer_callback(cb_id, "Уже получено!", True)
        return
    p = run(_get_player(uid))
    run(_update_player(uid, gold=p["gold"]+q["reward"]))
    run(_claim_quest_db(uid, qid))
    answer_callback(cb_id, f"🎁 +{q['reward']}💰 за «{q['name']}»!", True)
    handle_quests(uid, chat_id, message_id)


def handle_top(chat_id: int, message_id: int = None, cb_id: str = None):
    run(_init_db())
    players = run(_get_top(10))
    if not players:
        send_message(chat_id, "🏆 Нет игроков!", kb_back())
        return
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    text   = "🏆 <b>ТОП-10 ВОИНОВ</b>\n\n"
    for i, p in enumerate(players):
        name = p["full_name"] or p["username"] or f"#{p['user_id']}"
        wr   = p["wins"] / max(1, p["wins"]+p["losses"]) * 100
        text += (
            f"{medals[i] if i<10 else i+1} <b>{name}</b>\n"
            f"   Ур.{p['level']} | 🏟{p['arena_rating']} {_rank(p['arena_rating'])}"
            f" | ⚔️{p['wins']}W {wr:.0f}%\n\n"
        )
    total = run(_count("players"))
    text += f"👥 Всего игроков: {total}"
    if message_id:
        edit_message(chat_id, message_id, text, kb_back())
    else:
        send_message(chat_id, text, kb_back())
    if cb_id: answer_callback(cb_id)


# ══════════════════════════════════════════════════════════════
# 🔀 РОУТЕР АПДЕЙТОВ
# ══════════════════════════════════════════════════════════════

def route_message(msg: dict):
    text    = msg.get("text","")
    chat_id = msg["chat"]["id"]
    uid     = msg["from"]["id"]
    uname   = msg["from"].get("username","")
    fname   = msg["from"].get("first_name","") + " " + msg["from"].get("last_name","")
    fname   = fname.strip()

    if text.startswith("/start"):
        handle_start(uid, uname, fname, chat_id)
    elif text.startswith("/profile"):
        handle_profile(uid, chat_id)
    elif text.startswith("/battle"):
        handle_battle(uid, chat_id)
    elif text.startswith("/arena"):
        handle_battle(uid, chat_id, arena=True)
    elif text.startswith("/collection"):
        handle_collection(uid, chat_id)
    elif text.startswith("/gacha"):
        handle_gacha(uid, chat_id)
    elif text.startswith("/daily"):
        handle_daily(uid, chat_id)
    elif text.startswith("/shop"):
        handle_shop(uid, chat_id)
    elif text.startswith("/inventory"):
        handle_inventory(uid, chat_id)
    elif text.startswith("/quest"):
        handle_quests(uid, chat_id)
    elif text.startswith("/top"):
        handle_top(chat_id)
    elif text.startswith("/help"):
        send_message(chat_id, (
            "🍆 <b>КОМАНДЫ</b>\n\n"
            "/start — Меню\n/profile — Профиль\n"
            "/battle — Бой\n/arena — Арена\n"
            "/collection — Коллекция\n/gacha — Гача\n"
            "/daily — Ежедневка\n/shop — Магазин\n"
            "/inventory — Инвентарь\n/quest — Квесты\n"
            "/top — Топ\n/stats — Статистика"
        ), kb_back())
    elif text.startswith("/stats"):
        p = run(_count("players"))
        d = run(_count("dildos"))
        send_message(chat_id,
            f"📊 <b>Статистика</b>\n\n👥 Игроков: {p}\n🍆 Дилдаков: {d}",
            kb_back()
        )
    else:
        send_message(chat_id,
            "🍆 Используй кнопки или /help для списка команд!",
            kb_main()
        )


def route_callback(cb: dict):
    uid        = cb["from"]["id"]
    chat_id    = cb["message"]["chat"]["id"]
    message_id = cb["message"]["message_id"]
    cb_id      = cb["id"]
    data       = cb.get("data","")

    if data == "menu":
        edit_message(chat_id, message_id,
            "🍆 <b>БИТВА ДИЛДАКОВ</b> 🍆\n\nВыбирай действие:",
            kb_main()
        )
        answer_callback(cb_id)

    elif data == "profile":
        handle_profile(uid, chat_id, message_id, cb_id)

    elif data == "collection":
        handle_collection(uid, chat_id, message_id, cb_id, 0)

    elif data.startswith("colp_"):
        page = int(data.split("_")[1])
        handle_collection(uid, chat_id, message_id, cb_id, page)

    elif data.startswith("dildo_"):
        did = int(data.split("_")[1])
        handle_dildo_detail(uid, chat_id, message_id, cb_id, did)

    elif data.startswith("equip_"):
        did = int(data.split("_")[1])
        handle_equip(uid, chat_id, message_id, cb_id, did)

    elif data == "battle":
        handle_battle(uid, chat_id, message_id, cb_id, False)

    elif data == "arena":
        handle_battle(uid, chat_id, message_id, cb_id, True)

    elif data == "gacha":
        handle_gacha(uid, chat_id, message_id, cb_id)

    elif data == "daily":
        handle_daily(uid, chat_id, message_id, cb_id)

    elif data == "shop":
        handle_shop(uid, chat_id, message_id, cb_id)

    elif data.startswith("buy_"):
        handle_buy(uid, chat_id, message_id, cb_id, data[4:])

    elif data == "inventory":
        handle_inventory(uid, chat_id, message_id, cb_id)

    elif data.startswith("use_"):
        handle_use(uid, chat_id, message_id, cb_id, data[4:])

    elif data == "quests":
        handle_quests(uid, chat_id, message_id, cb_id)

    elif data.startswith("claim_"):
        handle_claim(uid, chat_id, message_id, cb_id, data[6:])

    elif data == "top":
        handle_top(chat_id, message_id, cb_id)

    else:
        answer_callback(cb_id, "🤔 Неизвестная команда")


def process_update(data: dict):
    """Главный роутер апдейтов"""
    try:
        if "message" in data:
            route_message(data["message"])
        elif "callback_query" in data:
            route_callback(data["callback_query"])
    except Exception as e:
        print(f"[ROUTE ERROR] {e}")


# ══════════════════════════════════════════════════════════════
# 🌐 VERCEL HANDLER
# ══════════════════════════════════════════════════════════════

class handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # тишина в логах

    def do_GET(self):
        """Установка вебхука"""
        result = set_webhook_sync(WEBHOOK_URL)
        ok     = result.get("ok", False)
        body   = (
            f"✅ Webhook установлен!\n→ {WEBHOOK_URL}"
            if ok else
            f"❌ Ошибка: {result}"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        """Приём апдейтов от Telegram"""
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        try:
            data = json.loads(body.decode("utf-8"))
            process_update(data)
        except Exception as e:
            print(f"[POST ERROR] {e}")

        # Всегда 200 — иначе Telegram будет слать повторно
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
