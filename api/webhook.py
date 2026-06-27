"""
🍆 БИТВА ДИЛДАКОВ 🍆
@Battledildaks_bot
Vercel Serverless Fix
"""

import os
import json
import random
import asyncio
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler

import aiosqlite
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Update, Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

# ══════════════════════════════════════════════════════════════
# 🔧 КОНФИГ
# ══════════════════════════════════════════════════════════════

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
DB_PATH = "/tmp/dildaks.db"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# ══════════════════════════════════════════════════════════════
# 🎨 КОНСТАНТЫ
# ══════════════════════════════════════════════════════════════

RARITIES = {
    "common":    {"name": "Обычный",      "emoji": "⚪", "mult": 1.0,  "chance": 45},
    "uncommon":  {"name": "Необычный",    "emoji": "🟢", "mult": 1.3,  "chance": 25},
    "rare":      {"name": "Редкий",       "emoji": "🔵", "mult": 1.7,  "chance": 15},
    "epic":      {"name": "Эпический",    "emoji": "🟣", "mult": 2.2,  "chance": 9},
    "legendary": {"name": "Легендарный",  "emoji": "🟡", "mult": 3.0,  "chance": 4},
    "mythic":    {"name": "Мифический",   "emoji": "🔴", "mult": 4.0,  "chance": 1.5},
    "divine":    {"name": "Божественный", "emoji": "💠", "mult": 6.0,  "chance": 0.5},
}

DILDO_NAMES = {
    "common":    ["Резиновый Новичок","Скромняга","Первый Опыт","Бюджетный Друг","Мягкий Утешитель","Силиконовый Валера","Гелевый Гена"],
    "uncommon":  ["Вибро-Бандит","Ребристый Разбойник","Двойной Удар","Турбо-Шалун","Присоска-Мастер","Пупырчатый Карл"],
    "rare":      ["Анаконда Страсти","Титановый Терминатор","Чёрная Мамба","Королевская Кобра","Двуглавый Дракон"],
    "epic":      ["Дилдо Хаоса","Вибро-Берсерк","Тёмный Властелин","Кристальный Разрушитель","Адская Гидра"],
    "legendary": ["Экскалибур Наслаждений","Мьёльнир Оргазмов","Жезл Посейдона","Священный Грааль","Скипетр Бездны"],
    "mythic":    ["Пожиратель Миров","Аннигилятор Целомудрия","Космический Опустошитель","Дилдо Древних Богов"],
    "divine":    ["ДИЛДО ВСЕЛЕННОЙ 🌌","АБСОЛЮТНЫЙ ОРГАЗМ ∞","БОЛЬШОЙ ВЗРЫВ 💥","СОЗДАТЕЛЬ МИРОВ 🌍"],
}

MATERIALS = [
    "силиконовый","латексный","стеклянный","металлический",
    "кристальный","ледяной","огненный","призрачный","алмазный",
    "из метеоритного железа","из тёмной материи","из лунного света",
]

ABILITIES = {
    "common":    [("Шлепок","💢",5,"шлёпает"),("Тычок","👉",7,"тычет"),("Вибрация","📳",6,"вибрирует")],
    "uncommon":  [("Двойной удар","💥",12,"бьёт дважды"),("Вихрь страсти","🌀",14,"кружит"),("Разряд","⚡",13,"бьёт током")],
    "rare":      [("Анальный торнадо","🌪",22,"закручивает"),("Оргазмический взрыв","💣",25,"взрывается"),("Пронзание","🗡",20,"пронзает")],
    "epic":      [("Цунами удовольствия","🌊",35,"накрывает волной"),("Тёмный ритуал","🔮",40,"ритуалит"),("Берсерк","😈",38,"бесится")],
    "legendary": [("Божественный оргазм","✨",55,"оргазмирует"),("Апокалипсис","☄️",60,"апокалиптит"),("Доминирование","👑",50,"доминирует")],
    "mythic":    [("Разрыв реальности","🕳",75,"рвёт реальность"),("Квантовый оргазм","⚛️",80,"квантует")],
    "divine":    [("БОЛЬШОЙ ВЗРЫВ","🌌",100,"пересоздаёт"),("∞ ЭКСТАЗ ∞","💠",120,"экстазирует")],
}

BATTLE_COMMENTS = [
    "{attacker} замахнулся «{dildo}» и {action} {defender}!",
    "«{dildo}» в руках {attacker} {action} {defender}!",
    "{attacker} крутанул «{dildo}» как вертолёт — {action} {defender}!",
    "С диким криком {attacker} обрушил «{dildo}» на {defender}!",
    "{attacker} подкрался с «{dildo}» — {action} {defender}!",
]

CRIT_COMMENTS = [
    "💥 КРИТИЧЕСКИЙ УДАР! Соседи вызвали полицию!",
    "💥 КРИТ! Сейсмологи зафиксировали толчок!",
    "💥 МОЩНЕЙШИЙ КРИТ! Даже дилдо удивился!",
    "💥 КРИТ В САМОЕ СЕРДЦЕ... почти!",
]

DODGE_COMMENTS = [
    "🌀 {defender} увернулся в последний момент!",
    "🌀 {defender} сделал сальто назад! Гимнаст!",
    "🌀 Мимо! {defender} скользкий!",
]

SHOP_ITEMS = {
    "heal_potion": {"name":"🧪 Смазка Исцеления","desc":"Восст. 50 HP","price":100,"effect":"heal","value":50},
    "mega_heal":   {"name":"💊 Виагра Богов","desc":"Полное восст. HP","price":500,"effect":"full_heal","value":0},
    "atk_boost":   {"name":"💪 Стероиды для Дилдо","desc":"+15 к атаке","price":800,"effect":"atk_boost","value":15},
    "crit_ring":   {"name":"💍 Кольцо Оргазма","desc":"+10% крита","price":600,"effect":"crit_boost","value":10},
    "gacha_ticket":{"name":"🎰 Лотерейный Билет","desc":"Крутануть гачу","price":300,"effect":"gacha","value":0},
}

QUEST_LIST = [
    {"id":"first_blood","name":"Первая кровь","desc":"Выиграй 1 бой","target":1,"reward":200,"type":"wins"},
    {"id":"killer","name":"Убийца","desc":"Выиграй 5 боёв","target":5,"reward":500,"type":"wins"},
    {"id":"destroyer","name":"Разрушитель","desc":"Выиграй 25 боёв","target":25,"reward":2000,"type":"wins"},
    {"id":"collector","name":"Коллекционер","desc":"Собери 5 дилдаков","target":5,"reward":800,"type":"dildos"},
    {"id":"rich","name":"Богатенький","desc":"Накопи 5000 монет","target":5000,"reward":1000,"type":"gold"},
    {"id":"lvl10","name":"Десятка","desc":"Достигни 10 уровня","target":10,"reward":1500,"type":"level"},
]

# ══════════════════════════════════════════════════════════════
# 🗄️ БАЗА ДАННЫХ
# ══════════════════════════════════════════════════════════════

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT    DEFAULT '',
                full_name   TEXT    DEFAULT '',
                level       INTEGER DEFAULT 1,
                exp         INTEGER DEFAULT 0,
                gold        INTEGER DEFAULT 500,
                gems        INTEGER DEFAULT 10,
                hp          INTEGER DEFAULT 100,
                max_hp      INTEGER DEFAULT 100,
                wins        INTEGER DEFAULT 0,
                losses      INTEGER DEFAULT 0,
                total_damage INTEGER DEFAULT 0,
                arena_rating INTEGER DEFAULT 1000,
                equipped_dildo_id INTEGER DEFAULT 0,
                last_daily  TEXT    DEFAULT '',
                last_gacha  TEXT    DEFAULT '',
                crit_bonus  INTEGER DEFAULT 0,
                atk_bonus   INTEGER DEFAULT 0,
                created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS dildos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id    INTEGER,
                name        TEXT,
                rarity      TEXT    DEFAULT 'common',
                material    TEXT    DEFAULT '',
                level       INTEGER DEFAULT 1,
                exp         INTEGER DEFAULT 0,
                base_atk    INTEGER DEFAULT 10,
                base_def    INTEGER DEFAULT 5,
                base_spd    INTEGER DEFAULT 5,
                hp          INTEGER DEFAULT 50,
                max_hp      INTEGER DEFAULT 50,
                crit_chance INTEGER DEFAULT 5,
                ability_name TEXT   DEFAULT '',
                ability_emoji TEXT  DEFAULT '',
                ability_dmg INTEGER DEFAULT 5,
                ability_desc TEXT   DEFAULT '',
                kills       INTEGER DEFAULT 0,
                created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
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
                completed INTEGER DEFAULT 0,
                claimed   INTEGER DEFAULT 0
            );
        """)
        await db.commit()


async def get_player(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM players WHERE user_id=?", (user_id,)
        ) as cur:
            return await cur.fetchone()


async def create_player(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO players (user_id,username,full_name) VALUES (?,?,?)",
            (user_id, username, full_name)
        )
        await db.commit()


async def update_player(user_id: int, **kwargs):
    if not kwargs:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        sets = ", ".join(f"{k}=?" for k in kwargs)
        vals = list(kwargs.values()) + [user_id]
        await db.execute(f"UPDATE players SET {sets} WHERE user_id=?", vals)
        await db.commit()


async def get_player_dildos(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM dildos WHERE owner_id=? ORDER BY base_atk DESC", (user_id,)
        ) as cur:
            return await cur.fetchall()


async def get_dildo(dildo_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM dildos WHERE id=?", (dildo_id,)
        ) as cur:
            return await cur.fetchone()


async def create_dildo(owner_id: int, rarity: str = None) -> dict:
    if not rarity:
        rarity = roll_rarity()
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
        cur = await db.execute(
            """INSERT INTO dildos
            (owner_id,name,rarity,material,base_atk,base_def,base_spd,
             hp,max_hp,crit_chance,ability_name,ability_emoji,ability_dmg,ability_desc)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (owner_id,name,rarity,mat,atk,dfn,spd,hp,hp,crit,ab[0],ab[1],ab[2],ab[3])
        )
        did = cur.lastrowid
        await db.commit()

    return {
        "id":did,"name":name,"rarity":rarity,"material":mat,
        "base_atk":atk,"base_def":dfn,"base_spd":spd,
        "hp":hp,"max_hp":hp,"crit_chance":crit,
        "ability_name":ab[0],"ability_emoji":ab[1],
        "ability_dmg":ab[2],"ability_desc":ab[3],
    }


async def add_item(user_id: int, item_id: str, qty: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id,quantity FROM inventory WHERE user_id=? AND item_id=?",
            (user_id, item_id)
        ) as cur:
            row = await cur.fetchone()
        if row:
            await db.execute(
                "UPDATE inventory SET quantity=quantity+? WHERE id=?", (qty, row[0])
            )
        else:
            await db.execute(
                "INSERT INTO inventory (user_id,item_id,quantity) VALUES (?,?,?)",
                (user_id, item_id, qty)
            )
        await db.commit()


async def use_item_db(user_id: int, item_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id,quantity FROM inventory WHERE user_id=? AND item_id=?",
            (user_id, item_id)
        ) as cur:
            row = await cur.fetchone()
        if row and row[1] > 0:
            await db.execute(
                "UPDATE inventory SET quantity=quantity-1 WHERE id=?", (row[0],)
            )
            await db.commit()
            return True
        return False


async def get_inventory_db(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM inventory WHERE user_id=? AND quantity>0", (user_id,)
        ) as cur:
            return await cur.fetchall()


async def get_quest_progress(user_id: int, quest_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM quest_progress WHERE user_id=? AND quest_id=?",
            (user_id, quest_id)
        ) as cur:
            return await cur.fetchone()


async def upsert_quest(user_id: int, quest_id: str, progress: int):
    async with aiosqlite.connect(DB_PATH) as db:
        row = await get_quest_progress(user_id, quest_id)
        if row:
            await db.execute(
                "UPDATE quest_progress SET progress=? WHERE user_id=? AND quest_id=?",
                (progress, user_id, quest_id)
            )
        else:
            await db.execute(
                "INSERT INTO quest_progress (user_id,quest_id,progress) VALUES (?,?,?)",
                (user_id, quest_id, progress)
            )
        await db.commit()


async def get_top_players(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM players ORDER BY arena_rating DESC LIMIT ?", (limit,)
        ) as cur:
            return await cur.fetchall()


async def count_stat(table: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(f"SELECT COUNT(*) FROM {table}") as cur:
            row = await cur.fetchone()
            return row[0]


# ══════════════════════════════════════════════════════════════
# 🎲 ИГРОВАЯ ЛОГИКА
# ══════════════════════════════════════════════════════════════

def roll_rarity() -> str:
    roll = random.uniform(0, 100)
    cum  = 0
    for rar, data in RARITIES.items():
        cum += data["chance"]
        if roll <= cum:
            return rar
    return "common"


def exp_for_level(lvl: int) -> int:
    return int(100 * (lvl ** 1.5))


def dildo_exp_for_level(lvl: int) -> int:
    return int(50 * (lvl ** 1.3))


async def add_exp(user_id: int, amount: int):
    p = await get_player(user_id)
    exp   = p["exp"] + amount
    level = p["level"]
    up    = False
    while exp >= exp_for_level(level):
        exp  -= exp_for_level(level)
        level += 1
        up    = True
    new_hp = 100 + (level - 1) * 15
    await update_player(user_id, exp=exp, level=level, max_hp=new_hp, hp=new_hp)
    return up, level


async def add_dildo_exp(dildo_id: int, amount: int):
    d = await get_dildo(dildo_id)
    if not d:
        return False, 0
    exp   = d["exp"] + amount
    level = d["level"]
    up    = False
    while exp >= dildo_exp_for_level(level):
        exp  -= dildo_exp_for_level(level)
        level += 1
        up    = True
    r   = RARITIES[d["rarity"]]
    atk = d["base_atk"] + int(2 * r["mult"]) * (level - d["level"])
    dfn = d["base_def"] + int(1 * r["mult"]) * (level - d["level"])
    hp  = d["max_hp"]  + int(5 * r["mult"]) * (level - d["level"])
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE dildos SET exp=?,level=?,base_atk=?,base_def=?,hp=?,max_hp=? WHERE id=?",
            (exp, level, atk, dfn, hp, hp, dildo_id)
        )
        await db.commit()
    return up, level


def generate_enemy(player_level: int) -> dict:
    level  = max(1, player_level + random.randint(-2, 3))
    rarity = roll_rarity()
    r      = RARITIES[rarity]
    names  = ["Безумный Вибратор","Дикий Фаллос","Резиновый Бандит",
               "Силиконовый Маньяк","Призрачный Хер","Демон Наслаждений",
               "Гоблин-Извращенец","Тролль с Дилдаком","Орк-Доминатор",
               "Суккуб Подворотни","Скелет-Онанист","Дракон-Нимфоман"]
    ab     = random.choice(ABILITIES[rarity])
    return {
        "name":        random.choice(names),
        "level":       level,
        "rarity":      rarity,
        "dildo_name":  random.choice(DILDO_NAMES[rarity]),
        "atk":         int((8  + level*3)  * r["mult"]),
        "defense":     int((3  + level*2)  * r["mult"]),
        "hp":          int((40 + level*12) * r["mult"]),
        "max_hp":      int((40 + level*12) * r["mult"]),
        "crit":        5 + int(r["mult"]*2),
        "ability_name":ab[0],"ability_emoji":ab[1],
        "ability_dmg": ab[2],"ability_desc": ab[3],
    }


async def simulate_battle(player_id: int, dildo_id: int, enemy: dict) -> dict:
    player = await get_player(player_id)
    dildo  = await get_dildo(dildo_id)
    if not dildo:
        return {"error": "Нет экипированного дилдо!"}

    p_name = player["full_name"] or player["username"] or f"Игрок"
    e_name = enemy["name"]

    p_hp   = dildo["max_hp"]
    e_hp   = enemy["hp"]
    p_atk  = dildo["base_atk"] + player["atk_bonus"]
    p_def  = dildo["base_def"]
    p_crit = dildo["crit_chance"] + player["crit_bonus"]
    e_atk  = enemy["atk"]
    e_def  = enemy["defense"]
    e_crit = enemy["crit"]

    log    = []
    rnd    = 0
    p_dmg  = 0
    e_dmg  = 0

    log.append(f"⚔️ <b>{p_name}</b> VS <b>{e_name}</b> (Ур.{enemy['level']})")
    log.append(f"🍆 «{dildo['name']}» VS «{enemy['dildo_name']}»")
    log.append(f"❤️ {p_hp} HP | ❤️ {e_hp} HP")
    log.append("━"*28)

    while p_hp > 0 and e_hp > 0 and rnd < 20:
        rnd += 1
        log.append(f"\n📍 <b>Раунд {rnd}</b>")

        # --- Ход игрока ---
        use_ab = random.random() < 0.3 and rnd > 1
        raw    = (dildo["ability_dmg"] + int(p_atk*0.5)) if use_ab else (p_atk + random.randint(-3,5))
        act    = f"{dildo['ability_emoji']} <b>{dildo['ability_name']}</b>!" if use_ab else \
                 random.choice(BATTLE_COMMENTS).format(
                     attacker=p_name, defender=e_name,
                     dildo=dildo["name"], action=dildo["ability_desc"]
                 )
        crit   = random.randint(1,100) <= p_crit
        if crit: raw = int(raw * 1.8)
        dodge  = random.randint(1,100) <= min(25, e_def//2)

        if dodge:
            log.append(random.choice(DODGE_COMMENTS).format(defender=e_name, dildo=dildo["name"]))
        else:
            dmg = max(1, raw - e_def//3)
            e_hp -= dmg; p_dmg += dmg
            log.append(f"  {act}")
            if crit: log.append(f"  {random.choice(CRIT_COMMENTS)}")
            log.append(f"  💔 -{dmg} HP → {e_name}: {max(0,e_hp)} HP")

        if e_hp <= 0:
            break

        # --- Ход врага ---
        use_ab_e = random.random() < 0.25
        raw_e    = (enemy["ability_dmg"] + int(e_atk*0.5)) if use_ab_e else (e_atk + random.randint(-3,5))
        act_e    = f"{enemy['ability_emoji']} <b>{enemy['ability_name']}</b>!" if use_ab_e else \
                   random.choice(BATTLE_COMMENTS).format(
                       attacker=e_name, defender=p_name,
                       dildo=enemy["dildo_name"], action=enemy["ability_desc"]
                   )
        crit_e   = random.randint(1,100) <= e_crit
        if crit_e: raw_e = int(raw_e * 1.8)
        dodge_e  = random.randint(1,100) <= min(25, p_def//2)

        if dodge_e:
            log.append(random.choice(DODGE_COMMENTS).format(defender=p_name, dildo=enemy["dildo_name"]))
        else:
            dmg_e = max(1, raw_e - p_def//3)
            p_hp -= dmg_e; e_dmg += dmg_e
            log.append(f"  {act_e}")
            if crit_e: log.append(f"  {random.choice(CRIT_COMMENTS)}")
            log.append(f"  💔 -{dmg_e} HP → {p_name}: {max(0,p_hp)} HP")

    log.append("\n" + "═"*28)
    won = p_hp > 0

    gold = int(30  * enemy["level"] * RARITIES[enemy["rarity"]]["mult"])
    xp   = int(25  * enemy["level"] * RARITIES[enemy["rarity"]]["mult"])
    dxp  = int(15  * enemy["level"] * RARITIES[enemy["rarity"]]["mult"])

    if won:
        log.append(f"🏆 <b>ПОБЕДА!</b> {p_name} уничтожил {e_name}!")
        log.append(f"💰 +{gold} золота | ⭐ +{xp} опыта | 📊 Урон: {p_dmg}")

        pdata = await get_player(player_id)
        await update_player(player_id,
            gold=pdata["gold"]+gold,
            wins=pdata["wins"]+1,
            total_damage=pdata["total_damage"]+p_dmg
        )
        up, lvl = await add_exp(player_id, xp)
        if up: log.append(f"🎉 <b>УРОВЕНЬ {lvl}!</b>")

        dup, dlvl = await add_dildo_exp(dildo_id, dxp)
        if dup: log.append(f"🍆✨ Дилдо вырос до {dlvl} уровня!")

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE dildos SET kills=kills+1 WHERE id=?", (dildo_id,))
            await db.commit()

        drop_ch = 15 + int(RARITIES[enemy["rarity"]]["mult"]*5)
        if random.randint(1,100) <= drop_ch:
            drop = await create_dildo(player_id, enemy["rarity"])
            r    = RARITIES[drop["rarity"]]
            log.append(f"\n🎁 <b>ДРОП!</b> {r['emoji']} «{drop['name']}» [{r['name']}]")
            log.append(f"  ⚔️{drop['base_atk']} 🛡{drop['base_def']}")

        pdata2 = await get_player(player_id)
        await upsert_quest(player_id, "first_blood", pdata2["wins"])
        await upsert_quest(player_id, "killer",      pdata2["wins"])
        await upsert_quest(player_id, "destroyer",   pdata2["wins"])
    else:
        log.append(f"💀 <b>ПОРАЖЕНИЕ!</b> Возвращайся сильнее!")
        log.append(f"⭐ +{int(xp*0.3)} опыта утешения | 📊 Урон: {p_dmg}")
        pdata = await get_player(player_id)
        await update_player(player_id,
            losses=pdata["losses"]+1,
            total_damage=pdata["total_damage"]+p_dmg
        )
        await add_exp(player_id, int(xp*0.3))

    return {"won":won, "log":"\n".join(log), "rounds":rnd}


# ══════════════════════════════════════════════════════════════
# ⌨️ КЛАВИАТУРЫ
# ══════════════════════════════════════════════════════════════

def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Профиль",    callback_data="profile"),
            InlineKeyboardButton(text="🍆 Коллекция",  callback_data="collection"),
        ],
        [
            InlineKeyboardButton(text="⚔️ В БОЙ!",    callback_data="battle"),
            InlineKeyboardButton(text="🏟 Арена",      callback_data="arena"),
        ],
        [
            InlineKeyboardButton(text="🎰 Гача",       callback_data="gacha"),
            InlineKeyboardButton(text="🎁 Ежедневка",  callback_data="daily"),
        ],
        [
            InlineKeyboardButton(text="🛒 Магазин",    callback_data="shop"),
            InlineKeyboardButton(text="🎒 Инвентарь",  callback_data="inventory"),
        ],
        [
            InlineKeyboardButton(text="📜 Квесты",     callback_data="quests"),
            InlineKeyboardButton(text="🏆 Топ",        callback_data="top"),
        ],
    ])


def kb_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Меню", callback_data="menu")]
    ])


def kb_after_battle() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚔️ Ещё!",  callback_data="battle"),
            InlineKeyboardButton(text="🔙 Меню",  callback_data="menu"),
        ]
    ])


def kb_collection(dildos, page: int = 0) -> InlineKeyboardMarkup:
    per  = 5
    sl   = dildos[page*per : page*per+per]
    btns = []
    for d in sl:
        r = RARITIES[d["rarity"]]
        btns.append([InlineKeyboardButton(
            text=f"{r['emoji']} {d['name']} Ур.{d['level']} ⚔️{d['base_atk']}",
            callback_data=f"dildo_{d['id']}"
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"colp_{page-1}"))
    if (page+1)*per < len(dildos):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"colp_{page+1}"))
    if nav:
        btns.append(nav)
    btns.append([InlineKeyboardButton(text="🔙 Меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


def kb_dildo(dildo_id: int, equipped: bool) -> InlineKeyboardMarkup:
    btns = []
    if not equipped:
        btns.append([InlineKeyboardButton(text="⚔️ Экипировать", callback_data=f"equip_{dildo_id}")])
    btns.append([InlineKeyboardButton(text="🔙 Коллекция", callback_data="collection")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


def kb_shop() -> InlineKeyboardMarkup:
    btns = [
        [InlineKeyboardButton(
            text=f"{i['name']} — 💰{i['price']}",
            callback_data=f"buy_{k}"
        )]
        for k, i in SHOP_ITEMS.items()
    ]
    btns.append([InlineKeyboardButton(text="🔙 Меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=btns)


# ══════════════════════════════════════════════════════════════
# 🛠 ХЕЛПЕРЫ
# ══════════════════════════════════════════════════════════════

async def send(event, text: str, kb=None):
    """edit для callback, answer для message"""
    kw = {"reply_markup": kb} if kb else {}
    try:
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(text, reply_markup=kb)
        else:
            await event.answer(text, **({"reply_markup": kb} if kb else {}))
    except Exception:
        target = event.message if isinstance(event, CallbackQuery) else event
        await target.answer(text, **({"reply_markup": kb} if kb else {}))


def rank_name(rating: int) -> str:
    if rating >= 2000: return "💎 Алмаз"
    if rating >= 1600: return "🥇 Золото"
    if rating >= 1300: return "🥈 Серебро"
    if rating >= 1000: return "🥉 Бронза"
    return "🪵 Дерево"


def exp_bar(cur, need, size=12) -> str:
    filled = int((cur / max(1,need)) * size)
    return "█"*filled + "░"*(size-filled)


# ══════════════════════════════════════════════════════════════
# 📨 ХЕНДЛЕРЫ
# ══════════════════════════════════════════════════════════════

@router.message(CommandStart())
async def h_start(msg: Message):
    await init_db()
    uid  = msg.from_user.id
    uname= msg.from_user.username or ""
    name = msg.from_user.full_name or ""

    player = await get_player(uid)
    if not player:
        await create_player(uid, uname, name)
        d = await create_dildo(uid, "common")
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE players SET equipped_dildo_id=? WHERE user_id=?",
                (d["id"], uid)
            )
            await db.commit()
        for q in QUEST_LIST:
            await upsert_quest(uid, q["id"], 0)

        r = RARITIES[d["rarity"]]
        text = (
            "🍆💥 <b>ДОБРО ПОЖАЛОВАТЬ В БИТВУ ДИЛДАКОВ!</b> 💥🍆\n\n"
            "Мир, где резиновые воины сражаются за честь и доминирование!\n\n"
            f"🎁 <b>Твой первый дилдак:</b>\n"
            f"{r['emoji']} <b>«{d['name']}»</b> [{r['name']}]\n"
            f"🔨 {d['material']}\n"
            f"⚔️{d['base_atk']} 🛡{d['base_def']} 💨{d['base_spd']} ❤️{d['hp']}\n"
            f"✨ {d['ability_emoji']} {d['ability_name']}\n\n"
            "<i>Вперёд к победам, воин!</i> 🍆⚔️"
        )
    else:
        await update_player(uid, username=uname, full_name=name)
        text = f"🍆 С возвращением, <b>{name}</b>!\n\nГотов к битвам?"

    await msg.answer(text, reply_markup=kb_main())


@router.message(Command("help"))
async def h_help(msg: Message):
    text = (
        "🍆 <b>БИТВА ДИЛДАКОВ — КОМАНДЫ</b>\n\n"
        "/start — Начать / вернуться в меню\n"
        "/profile — Профиль\n"
        "/collection — Коллекция дилдаков\n"
        "/battle — Бой с врагом\n"
        "/gacha — Крутануть гачу\n"
        "/daily — Ежедневная награда\n"
        "/shop — Магазин\n"
        "/inventory — Инвентарь\n"
        "/quest — Квесты\n"
        "/top — Топ игроков\n"
        "/stats — Статистика\n"
    )
    await msg.answer(text, reply_markup=kb_back())


@router.message(Command("profile"))
async def h_profile_cmd(msg: Message):
    await show_profile(msg, msg.from_user.id)


@router.message(Command("battle"))
async def h_battle_cmd(msg: Message):
    await do_battle(msg, msg.from_user.id)


@router.message(Command("collection"))
async def h_col_cmd(msg: Message):
    await show_collection(msg, msg.from_user.id)


@router.message(Command("shop"))
async def h_shop_cmd(msg: Message):
    await show_shop(msg, msg.from_user.id)


@router.message(Command("daily"))
async def h_daily_cmd(msg: Message):
    await do_daily(msg, msg.from_user.id)


@router.message(Command("gacha"))
async def h_gacha_cmd(msg: Message):
    await do_gacha(msg, msg.from_user.id)


@router.message(Command("quest"))
async def h_quest_cmd(msg: Message):
    await show_quests(msg, msg.from_user.id)


@router.message(Command("top"))
async def h_top_cmd(msg: Message):
    await show_top(msg)


@router.message(Command("inventory"))
async def h_inv_cmd(msg: Message):
    await show_inventory(msg, msg.from_user.id)


@router.message(Command("stats"))
async def h_stats_cmd(msg: Message):
    p = await count_stat("players")
    d = await count_stat("dildos")
    await msg.answer(
        f"📊 <b>Статистика</b>\n\n👥 Игроков: {p}\n🍆 Дилдаков: {d}",
        reply_markup=kb_back()
    )


# ── Callback handlers ──────────────────────────────────────────

@router.callback_query(F.data == "menu")
async def cb_menu(cb: CallbackQuery):
    await cb.message.edit_text(
        "🍆 <b>БИТВА ДИЛДАКОВ</b> 🍆\n\nВыбирай действие:",
        reply_markup=kb_main()
    )


@router.callback_query(F.data == "profile")
async def cb_profile(cb: CallbackQuery):
    await show_profile(cb, cb.from_user.id)


@router.callback_query(F.data == "collection")
async def cb_col(cb: CallbackQuery):
    await show_collection(cb, cb.from_user.id)


@router.callback_query(F.data.startswith("colp_"))
async def cb_colp(cb: CallbackQuery):
    page   = int(cb.data.split("_")[1])
    dildos = await get_player_dildos(cb.from_user.id)
    await cb.message.edit_text(
        f"🍆 <b>КОЛЛЕКЦИЯ</b> — {len(dildos)} шт.",
        reply_markup=kb_collection(dildos, page)
    )


@router.callback_query(F.data.startswith("dildo_"))
async def cb_dildo(cb: CallbackQuery):
    did    = int(cb.data.split("_")[1])
    dildo  = await get_dildo(did)
    if not dildo:
        await cb.answer("Дилдо не найден!")
        return
    player = await get_player(cb.from_user.id)
    r      = RARITIES[dildo["rarity"]]
    eq     = player["equipped_dildo_id"] == did
    need   = dildo_exp_for_level(dildo["level"])
    text   = (
        f"{r['emoji']} <b>«{dildo['name']}»</b> {'⚔️ ЭКИПИРОВАН' if eq else ''}\n\n"
        f"📦 {r['name']} {r['emoji']}\n"
        f"🔨 {dildo['material']}\n"
        f"📊 Уровень {dildo['level']} | "
        f"[{exp_bar(dildo['exp'],need,10)}] {dildo['exp']}/{need}\n\n"
        f"⚔️ ATK: <b>{dildo['base_atk']}</b>\n"
        f"🛡 DEF: <b>{dildo['base_def']}</b>\n"
        f"💨 SPD: <b>{dildo['base_spd']}</b>\n"
        f"❤️ HP: <b>{dildo['hp']}/{dildo['max_hp']}</b>\n"
        f"🎯 Крит: <b>{dildo['crit_chance']}%</b>\n\n"
        f"✨ {dildo['ability_emoji']} <b>{dildo['ability_name']}</b>\n"
        f"   <i>{dildo['ability_desc']}</i> (💥{dildo['ability_dmg']})\n\n"
        f"💀 Убийств: {dildo['kills']}"
    )
    await cb.message.edit_text(text, reply_markup=kb_dildo(did, eq))


@router.callback_query(F.data.startswith("equip_"))
async def cb_equip(cb: CallbackQuery):
    did   = int(cb.data.split("_")[1])
    dildo = await get_dildo(did)
    if not dildo or dildo["owner_id"] != cb.from_user.id:
        await cb.answer("Не твой дилдо!")
        return
    await update_player(cb.from_user.id, equipped_dildo_id=did)
    r = RARITIES[dildo["rarity"]]
    await cb.answer(f"✅ Экипирован: {r['emoji']} «{dildo['name']}»!")
    # обновим карточку
    player = await get_player(cb.from_user.id)
    need   = dildo_exp_for_level(dildo["level"])
    text   = (
        f"{r['emoji']} <b>«{dildo['name']}»</b> ⚔️ ЭКИПИРОВАН\n\n"
        f"📦 {r['name']} | 🔨 {dildo['material']}\n"
        f"📊 Уровень {dildo['level']}\n\n"
        f"⚔️{dildo['base_atk']} 🛡{dildo['base_def']} ❤️{dildo['hp']}/{dildo['max_hp']}"
    )
    await cb.message.edit_text(text, reply_markup=kb_dildo(did, True))


@router.callback_query(F.data == "battle")
async def cb_battle(cb: CallbackQuery):
    await do_battle(cb, cb.from_user.id)


@router.callback_query(F.data == "arena")
async def cb_arena(cb: CallbackQuery):
    await do_battle(cb, cb.from_user.id, arena=True)


@router.callback_query(F.data == "gacha")
async def cb_gacha(cb: CallbackQuery):
    await do_gacha(cb, cb.from_user.id)


@router.callback_query(F.data == "daily")
async def cb_daily(cb: CallbackQuery):
    await do_daily(cb, cb.from_user.id)


@router.callback_query(F.data == "shop")
async def cb_shop(cb: CallbackQuery):
    await show_shop(cb, cb.from_user.id)


@router.callback_query(F.data.startswith("buy_"))
async def cb_buy(cb: CallbackQuery):
    await buy_item(cb, cb.from_user.id, cb.data[4:])


@router.callback_query(F.data == "inventory")
async def cb_inv(cb: CallbackQuery):
    await show_inventory(cb, cb.from_user.id)


@router.callback_query(F.data.startswith("use_"))
async def cb_use(cb: CallbackQuery):
    await use_item_handler(cb, cb.from_user.id, cb.data[4:])


@router.callback_query(F.data == "quests")
async def cb_quests(cb: CallbackQuery):
    await show_quests(cb, cb.from_user.id)


@router.callback_query(F.data.startswith("claim_"))
async def cb_claim(cb: CallbackQuery):
    await claim_quest(cb, cb.from_user.id, cb.data[6:])


@router.callback_query(F.data == "top")
async def cb_top(cb: CallbackQuery):
    await show_top(cb)


# ══════════════════════════════════════════════════════════════
# 🎮 ФУНКЦИИ ГЕЙМПЛЕЯ
# ══════════════════════════════════════════════════════════════

async def show_profile(event, uid: int):
    await init_db()
    p = await get_player(uid)
    if not p:
        await send(event, "❌ Сначала /start!", kb_back())
        return
    dildos = await get_player_dildos(uid)
    dildo  = await get_dildo(p["equipped_dildo_id"]) if p["equipped_dildo_id"] else None
    total  = p["wins"] + p["losses"]
    wr     = p["wins"] / max(1, total) * 100
    need   = exp_for_level(p["level"])

    text = (
        f"👤 <b>ПРОФИЛЬ</b>\n\n"
        f"🏷 {p['full_name'] or p['username'] or 'Аноним'}\n"
        f"📊 Уровень: <b>{p['level']}</b>\n"
        f"📈 [{exp_bar(p['exp'],need)}] {p['exp']}/{need}\n\n"
        f"💰 {p['gold']} | 💎 {p['gems']}\n\n"
        f"⚔️ Побед: <b>{p['wins']}</b> | 💀 Поражений: <b>{p['losses']}</b>\n"
        f"📊 Винрейт: <b>{wr:.1f}%</b> | 💥 Урон: <b>{p['total_damage']}</b>\n\n"
        f"🏟 Рейтинг: <b>{p['arena_rating']}</b> {rank_name(p['arena_rating'])}\n"
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
    await send(event, text, kb_back())


async def show_collection(event, uid: int):
    await init_db()
    dildos = await get_player_dildos(uid)
    if not dildos:
        await send(event, "😔 Коллекция пуста. /start", kb_back())
        return
    await send(event,
        f"🍆 <b>КОЛЛЕКЦИЯ</b> — {len(dildos)} шт.\nНажми на дилдак:",
        kb_collection(dildos, 0)
    )


async def do_battle(event, uid: int, arena: bool = False):
    await init_db()
    p = await get_player(uid)
    if not p:
        await send(event, "❌ /start", kb_back())
        return
    if not p["equipped_dildo_id"]:
        await send(event, "⚠️ Нет экипированного дилдо!\n/collection → выбери и экипируй.", kb_back())
        return

    enemy = generate_enemy(p["level"])
    r     = RARITIES[enemy["rarity"]]
    intro = (
        f"⚔️💥 <b>{'АРЕНА' if arena else 'БОЙ'}!</b>\n\n"
        f"VS <b>{enemy['name']}</b> (Ур.{enemy['level']})\n"
        f"{r['emoji']} «{enemy['dildo_name']}» [{r['name']}]\n"
        f"⚔️{enemy['atk']} 🛡{enemy['defense']} ❤️{enemy['hp']}\n\n"
        f"<i>Бой идёт...</i> 🔄"
    )
    await send(event, intro)

    result = await simulate_battle(uid, p["equipped_dildo_id"], enemy)
    if "error" in result:
        await send(event, f"❌ {result['error']}", kb_back())
        return

    if arena:
        p2 = await get_player(uid)
        if result["won"]:
            ch = random.randint(15, 35)
            await update_player(uid, arena_rating=p2["arena_rating"]+ch)
            result["log"] += f"\n🏟 Рейтинг: +{ch} → {p2['arena_rating']+ch}"
        else:
            ch = random.randint(10, 25)
            nr = max(0, p2["arena_rating"]-ch)
            await update_player(uid, arena_rating=nr)
            result["log"] += f"\n🏟 Рейтинг: -{ch} → {nr}"

    log = result["log"]
    if len(log) > 4000:
        log = log[:3900] + "\n\n...(слишком эпично для одного сообщения)"

    target = event.message if isinstance(event, CallbackQuery) else event
    await target.answer(log, reply_markup=kb_after_battle())


async def do_gacha(event, uid: int):
    await init_db()
    p = await get_player(uid)
    if not p:
        await send(event, "❌ /start", kb_back())
        return

    now = datetime.now()
    if p["last_gacha"]:
        diff = now - datetime.fromisoformat(p["last_gacha"])
        if diff < timedelta(hours=4):
            rem  = timedelta(hours=4) - diff
            h, m = rem.seconds//3600, (rem.seconds%3600)//60
            await send(event,
                f"⏳ Гача через <b>{h}ч {m}мин</b>\n\nКупи 🎰 Лотерейный Билет в /shop",
                kb_back()
            )
            return

    await update_player(uid, last_gacha=now.isoformat())
    d = await create_dildo(uid)
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
    dildos = await get_player_dildos(uid)
    await upsert_quest(uid, "collector", len(dildos))
    await send(event, text, kb_back())


async def do_daily(event, uid: int):
    await init_db()
    p   = await get_player(uid)
    if not p:
        await send(event, "❌ /start", kb_back())
        return
    now = datetime.now().date().isoformat()
    if p["last_daily"] == now:
        await send(event, "⏳ Ежедневка уже получена. Приходи завтра 🌅", kb_back())
        return

    gold = random.randint(100, 300) + p["level"] * 20
    gems = random.randint(1, 5)
    xp   = random.randint(30, 80)  + p["level"] * 10

    await update_player(uid, last_daily=now, gold=p["gold"]+gold, gems=p["gems"]+gems)
    up, lvl = await add_exp(uid, xp)

    text = (
        f"🎁 <b>ЕЖЕДНЕВНАЯ НАГРАДА!</b>\n\n"
        f"💰 +{gold} золота\n"
        f"💎 +{gems} гемов\n"
        f"⭐ +{xp} опыта\n"
    )
    if up:
        text += f"\n🎉 <b>УРОВЕНЬ {lvl}!</b>"
    if random.random() < 0.10:
        dd = await create_dildo(uid)
        rr = RARITIES[dd["rarity"]]
        text += f"\n\n🎊 <b>БОНУС!</b> {rr['emoji']} «{dd['name']}» [{rr['name']}]"
    text += "\n\n<i>Приходи завтра!</i>"
    await send(event, text, kb_back())


async def show_shop(event, uid: int):
    await init_db()
    p = await get_player(uid)
    if not p:
        await send(event, "❌ /start", kb_back())
        return
    text = (
        f"🛒 <b>МАГАЗИН</b>\n\n"
        f"💰 {p['gold']} | 💎 {p['gems']}\n\n"
    )
    for item in SHOP_ITEMS.values():
        text += f"{item['name']}\n  <i>{item['desc']}</i>\n\n"
    await send(event, text, kb_shop())


async def buy_item(cb: CallbackQuery, uid: int, item_id: str):
    if item_id not in SHOP_ITEMS:
        await cb.answer("❌ Нет такого товара!")
        return
    p    = await get_player(uid)
    item = SHOP_ITEMS[item_id]
    if p["gold"] < item["price"]:
        await cb.answer(f"❌ Нужно {item['price']}💰, у тебя {p['gold']}", show_alert=True)
        return

    await update_player(uid, gold=p["gold"]-item["price"])

    if item["effect"] == "gacha":
        d = await create_dildo(uid)
        r = RARITIES[d["rarity"]]
        await cb.answer(f"🎰 {r['emoji']} «{d['name']}»!", show_alert=True)
    elif item["effect"] == "heal":
        p2 = await get_player(uid)
        await update_player(uid, hp=min(p2["max_hp"], p2["hp"]+item["value"]))
        await cb.answer(f"💚 +{item['value']} HP!", show_alert=True)
    elif item["effect"] == "full_heal":
        p2 = await get_player(uid)
        await update_player(uid, hp=p2["max_hp"])
        await cb.answer("💚 HP полностью!", show_alert=True)
    elif item["effect"] == "atk_boost":
        p2 = await get_player(uid)
        await update_player(uid, atk_bonus=p2["atk_bonus"]+item["value"])
        await cb.answer(f"💪 +{item['value']} ATK навсегда!", show_alert=True)
    elif item["effect"] == "crit_boost":
        p2 = await get_player(uid)
        await update_player(uid, crit_bonus=p2["crit_bonus"]+item["value"])
        await cb.answer(f"🎯 +{item['value']}% крита!", show_alert=True)
    else:
        await add_item(uid, item_id)
        await cb.answer(f"✅ {item['name']} куплено!", show_alert=True)

    await show_shop(cb, uid)


async def show_inventory(event, uid: int):
    await init_db()
    items = await get_inventory_db(uid)
    if not items:
        await send(event, "🎒 Инвентарь пуст! /shop", kb_back())
        return
    text = "🎒 <b>ИНВЕНТАРЬ</b>\n\n"
    btns = []
    for item in items:
        si = SHOP_ITEMS.get(item["item_id"])
        if si:
            text += f"{si['name']} x{item['quantity']}\n  <i>{si['desc']}</i>\n\n"
            btns.append([InlineKeyboardButton(
                text=f"Использовать {si['name']}",
                callback_data=f"use_{item['item_id']}"
            )])
    btns.append([InlineKeyboardButton(text="🔙 Меню", callback_data="menu")])
    await send(event, text, InlineKeyboardMarkup(inline_keyboard=btns))


async def use_item_handler(cb: CallbackQuery, uid: int, item_id: str):
    ok = await use_item_db(uid, item_id)
    if not ok:
        await cb.answer("❌ Нет предмета!", show_alert=True)
        return
    item = SHOP_ITEMS.get(item_id)
    if not item:
        return
    p = await get_player(uid)
    if item["effect"] == "heal":
        new_hp = min(p["max_hp"], p["hp"]+item["value"])
        await update_player(uid, hp=new_hp)
        await cb.answer(f"💚 +{item['value']} HP → {new_hp}/{p['max_hp']}", show_alert=True)
    elif item["effect"] == "full_heal":
        await update_player(uid, hp=p["max_hp"])
        await cb.answer(f"💚 Полное восстановление!", show_alert=True)
    await show_inventory(cb, uid)


async def show_quests(event, uid: int):
    await init_db()
    text = "📜 <b>КВЕСТЫ</b>\n\n"
    btns = []
    for q in QUEST_LIST:
        pr  = await get_quest_progress(uid, q["id"])
        cur = pr["progress"] if pr else 0
        cl  = bool(pr["claimed"]) if pr else False
        done= cur >= q["target"]
        icon= "✅" if cl else ("🎁" if done else "🔄")
        bar = exp_bar(cur, q["target"], 8)
        text += (
            f"{icon} <b>{q['name']}</b>\n"
            f"   {q['desc']}\n"
            f"   [{bar}] {cur}/{q['target']} | 💰{q['reward']}\n\n"
        )
        if done and not cl:
            btns.append([InlineKeyboardButton(
                text=f"🎁 Забрать: {q['name']}",
                callback_data=f"claim_{q['id']}"
            )])
    btns.append([InlineKeyboardButton(text="🔙 Меню", callback_data="menu")])
    await send(event, text, InlineKeyboardMarkup(inline_keyboard=btns))


async def claim_quest(cb: CallbackQuery, uid: int, quest_id: str):
    q  = next((x for x in QUEST_LIST if x["id"]==quest_id), None)
    if not q:
        await cb.answer("Квест не найден!")
        return
    pr = await get_quest_progress(uid, quest_id)
    if not pr or pr["progress"] < q["target"]:
        await cb.answer("Квест не выполнен!", show_alert=True)
        return
    if pr["claimed"]:
        await cb.answer("Уже получено!", show_alert=True)
        return
    p = await get_player(uid)
    await update_player(uid, gold=p["gold"]+q["reward"])
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE quest_progress SET claimed=1 WHERE user_id=? AND quest_id=?",
            (uid, quest_id)
        )
        await db.commit()
    await cb.answer(f"🎁 +{q['reward']}💰 за «{q['name']}»!", show_alert=True)
    await show_quests(cb, uid)


async def show_top(event):
    await init_db()
    players = await get_top_players(10)
    if not players:
        await send(event, "🏆 Нет игроков!", kb_back())
        return
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    text = "🏆 <b>ТОП-10</b>\n\n"
    for i, p in enumerate(players):
        name = p["full_name"] or p["username"] or f"#{p['user_id']}"
        wr   = p["wins"]/max(1,p["wins"]+p["losses"])*100
        text += (
            f"{medals[i] if i<10 else i+1} <b>{name}</b>\n"
            f"   Ур.{p['level']} | 🏟{p['arena_rating']} | "
            f"⚔️{p['wins']}W {wr:.0f}%\n\n"
        )
    total = await count_stat("players")
    text += f"👥 Всего: {total}"
    await send(event, text, kb_back())


# ══════════════════════════════════════════════════════════════
# 🌐 VERCEL HANDLER
# ══════════════════════════════════════════════════════════════

async def process_update(data: dict):
    await init_db()
    update = Update(**data)
    await dp.feed_update(bot, update)


async def setup_webhook():
    await bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )


class handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # отключаем лишние логи

    def do_GET(self):
        """
        GET / → устанавливает вебхук и возвращает статус
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(setup_webhook())
            loop.close()
            body = f"✅ Webhook OK → {WEBHOOK_URL}".encode()
            code = 200
        except Exception as e:
            body = f"❌ Error: {e}".encode()
            code = 500

        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        """
        POST → получаем апдейт от Telegram
        """
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        try:
            data = json.loads(body.decode("utf-8"))
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(process_update(data))
            loop.close()
            code = 200
        except Exception as e:
            print(f"[ERROR] {e}")
            code = 200  # всегда 200 чтобы TG не спамил повторами

        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
