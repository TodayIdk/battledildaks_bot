"""
🍆 БИТВА ДИЛДАКОВ 🍆
Telegram Bot: @Battledildaks_bot
Версия: 1.0 ULTIMATE
Качество: 100%
Стиль: Жёсткий 18+ без цензуры

Один файл. Vercel. Полный угар.
"""

import os
import json
import random
import time
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from http.server import BaseHTTPRequestHandler

import aiosqlite
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Update, Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    BufBufferedInputFile
)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

# ══════════════════════════════════════════════════════════════
# 🔧 КОНФИГ
# ══════════════════════════════════════════════════════════════

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
DB_PATH = "/tmp/battledildaks.db"

bot = Bot(token=BOT_TOKEN, default={"parse_mode": "HTML"})
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# ══════════════════════════════════════════════════════════════
# 🎨 КОНСТАНТЫ И ДАННЫЕ ИГРЫ
# ══════════════════════════════════════════════════════════════

RARITIES = {
    "common":    {"name": "Обычный",      "emoji": "⚪", "color": "серый",    "mult": 1.0,  "chance": 45},
    "uncommon":  {"name": "Необычный",    "emoji": "🟢", "color": "зелёный",  "mult": 1.3,  "chance": 25},
    "rare":      {"name": "Редкий",       "emoji": "🔵", "color": "синий",    "mult": 1.7,  "chance": 15},
    "epic":      {"name": "Эпический",    "emoji": "🟣", "color": "фиолет",   "mult": 2.2,  "chance": 9},
    "legendary": {"name": "Легендарный",  "emoji": "🟡", "color": "золотой",  "mult": 3.0,  "chance": 4},
    "mythic":    {"name": "Мифический",   "emoji": "🔴", "color": "красный",  "mult": 4.0,  "chance": 1.5},
    "divine":    {"name": "Божественный", "emoji": "💠", "color": "алмазный", "mult": 6.0,  "chance": 0.5},
}

DILDO_NAMES = {
    "common": [
        "Резиновый Новичок", "Скромняга", "Первый Опыт", "Бюджетный Друг",
        "Мягкий Утешитель", "Тихий Шалун", "Нежный Пупсик", "Базовый Инстинкт",
        "Простой Парень", "Дешёвый Кайф", "Силиконовый Валера", "Гелевый Гена",
    ],
    "uncommon": [
        "Вибро-Бандит", "Ребристый Разбойник", "Двойной Удар", "Турбо-Шалун",
        "Присоска-Мастер", "Гибкий Философ", "Неоновый Грешник", "Пупырчатый Карл",
        "Светящийся Стыд", "Водонепроницаемый Ванька",
    ],
    "rare": [
        "Анаконда Страсти", "Титановый Терминатор", "Чёрная Мамба",
        "Королевская Кобра", "Бархатный Палач", "Пульсирующий Демон",
        "Двуглавый Дракон", "Спиральный Безумец", "Рогатый Воин",
    ],
    "epic": [
        "Дилдо Хаоса", "Вибро-Берсерк", "Тёмный Властелин", "Кристальный Разрушитель",
        "Адская Гидра", "Плазменный Фантом", "Ядовитый Искуситель", "Грозовой Молот",
    ],
    "legendary": [
        "Экскалибур Наслаждений", "Мьёльнир Оргазмов", "Жезл Посейдона",
        "Священный Грааль", "Копьё Судьбы", "Клинок Экстаза", "Скипетр Бездны",
    ],
    "mythic": [
        "Пожиратель Миров", "Аннигилятор Целомудрия", "Космический Опустошитель",
        "Дилдо Древних Богов", "Квантовый Разрыватель", "Тёмная Материя Страсти",
    ],
    "divine": [
        "ДИЛДО ВСЕЛЕННОЙ 🌌", "АБСОЛЮТНЫЙ ОРГАЗМ ∞", "АЛЬФА И ОМЕГА 💫",
        "БОЛЬШОЙ ВЗРЫВ 💥", "СОЗДАТЕЛЬ МИРОВ 🌍",
    ],
}

MATERIALS = [
    "силиконовый", "латексный", "стеклянный", "металлический", "деревянный",
    "кожаный", "кристальный", "ледяной", "огненный", "ядовитый",
    "призрачный", "алмазный", "из метеоритного железа", "из слёз девственниц",
    "из сгущённого лунного света", "из застывшей лавы", "из тёмной материи",
]

ABILITIES = {
    "common": [
        ("Шлепок", "💢", 5, "шлёпает по щеке"),
        ("Тычок", "👉", 7, "неуклюже тычет"),
        ("Вибрация", "📳", 6, "слабо вибрирует"),
    ],
    "uncommon": [
        ("Двойной удар", "💥", 12, "бьёт дважды"),
        ("Вихрь страсти", "🌀", 14, "создаёт вихрь"),
        ("Шоковый разряд", "⚡", 13, "бьёт током"),
    ],
    "rare": [
        ("Анальный торнадо", "🌪", 22, "создаёт торнадо в заднице"),
        ("Оргазмический взрыв", "💣", 25, "взрывается оргазмом"),
        ("Проникающий удар", "🗡", 20, "пронзает насквозь"),
    ],
    "epic": [
        ("Цунами удовольствия", "🌊", 35, "накрывает волной кайфа"),
        ("Тёмный ритуал", "🔮", 40, "призывает тёмные силы"),
        ("Берсерк-режим", "😈", 38, "впадает в ярость"),
    ],
    "legendary": [
        ("Божественный оргазм", "✨", 55, "дарует божественный оргазм"),
        ("Апокалипсис", "☄️", 60, "вызывает конец света"),
        ("Абсолютное доминирование", "👑", 50, "полностью доминирует"),
    ],
    "mythic": [
        ("Разрыв реальности", "🕳", 75, "разрывает ткань реальности"),
        ("Квантовый оргазм", "⚛️", 80, "оргазм во всех вселенных"),
    ],
    "divine": [
        ("БОЛЬШОЙ ВЗРЫВ", "🌌", 100, "пересоздаёт вселенную"),
        ("∞ ЭКСТАЗ ∞", "💠", 120, "бесконечный экстаз"),
    ],
}

BATTLE_COMMENTS = [
    "{attacker} яростно замахнулся «{dildo}» и {action} {defender}!",
    "«{dildo}» в руках {attacker} засветился и {action} {defender}!",
    "{attacker} крутанул «{dildo}» как вертолёт и {action} {defender}!",
    "С диким криком {attacker} обрушил «{dildo}» — {action} {defender}!",
    "{attacker} подкрался сзади с «{dildo}» и {action} {defender}!",
    "«{dildo}» задрожал от ярости и {action} {defender}!",
    "{attacker} метнул «{dildo}» как копьё — {action} {defender}!",
    "Земля содрогнулась, когда {attacker} ударил «{dildo}» по {defender}!",
]

CRIT_COMMENTS = [
    "💥 КРИТИЧЕСКИЙ УДАР! Соседи вызвали полицию!",
    "💥 КРИТ! У {defender} искры из глаз!",
    "💥 МОЩНЕЙШИЙ КРИТ! Сейсмологи зафиксировали толчок!",
    "💥 КРИТ В САМОЕ СЕРДЦЕ... ну, почти в сердце!",
    "💥 РАЗРУШИТЕЛЬНЫЙ КРИТ! Даже дилдо удивился!",
]

DODGE_COMMENTS = [
    "🌀 {defender} увернулся в последний момент! Ловкий сукин сын!",
    "🌀 {defender} сделал сальто назад! Гимнаст, бля!",
    "🌀 {defender} присел — «{dildo}» просвистел над головой!",
    "🌀 Мимо! {defender} скользкий как намазанный!",
]

SHOP_ITEMS = {
    "heal_potion": {
        "name": "🧪 Смазка Исцеления",
        "desc": "Восстанавливает 50 HP",
        "price": 100,
        "effect": "heal",
        "value": 50,
    },
    "mega_heal": {
        "name": "💊 Виагра Богов",
        "desc": "Восстанавливает 100% HP",
        "price": 500,
        "effect": "full_heal",
        "value": 0,
    },
    "atk_boost": {
        "name": "💪 Стероиды для Дилдо",
        "desc": "+15% к атаке навсегда",
        "price": 800,
        "effect": "atk_boost",
        "value": 15,
    },
    "crit_ring": {
        "name": "💍 Кольцо Оргазма",
        "desc": "+10% шанс крита",
        "price": 600,
        "effect": "crit_boost",
        "value": 10,
    },
    "gacha_ticket": {
        "name": "🎰 Лотерейный Билет",
        "desc": "Крутануть гачу (шанс на топ дилдо)",
        "price": 300,
        "effect": "gacha",
        "value": 0,
    },
    "rename_scroll": {
        "name": "📜 Свиток Переименования",
        "desc": "Дай дилдо новое имя",
        "price": 200,
        "effect": "rename",
        "value": 0,
    },
}

QUEST_LIST = [
    {"id": "first_blood",  "name": "Первая кровь",     "desc": "Выиграй 1 бой",      "target": 1,  "reward": 200,  "type": "wins"},
    {"id": "killer",       "name": "Убийца",            "desc": "Выиграй 5 боёв",      "target": 5,  "reward": 500,  "type": "wins"},
    {"id": "destroyer",    "name": "Разрушитель",       "desc": "Выиграй 25 боёв",     "target": 25, "reward": 2000, "type": "wins"},
    {"id": "collector",    "name": "Коллекционер",      "desc": "Собери 5 дилдаков",   "target": 5,  "reward": 800,  "type": "dildos"},
    {"id": "rich",         "name": "Богатенький",       "desc": "Накопи 5000 монет",   "target": 5000,"reward": 1000,"type": "gold"},
    {"id": "lvl10",        "name": "Десятка",           "desc": "Достигни 10 уровня",  "target": 10, "reward": 1500, "type": "level"},
]

WELCOME_TEXT = """
🍆💥 <b>ДОБРО ПОЖАЛОВАТЬ В БИТВУ ДИЛДАКОВ!</b> 💥🍆

Это мир, где резиновые воины сражаются за честь,
славу и доминирование!

<b>Тебе выдан стартовый дилдак!</b>
Прокачивай его, сражайся с другими игроками,
собирай коллекцию и стань <b>КОРОЛЁМ ДИЛДАКОВ!</b>

⚔️ Используй /help чтобы узнать команды
"""

HELP_TEXT = """
🍆 <b>БИТВА ДИЛДАКОВ — КОМАНДЫ</b> 🍆

👤 <b>Профиль:</b>
/start — Начать игру / Перезайти
/profile — Твой профиль
/collection — Твоя коллекция дилдаков
/equip — Экипировать дилдо

⚔️ <b>Бои:</b>
/battle — Бой с рандомным ИИ-врагом
/pvp — PvP бой (в разработке)
/arena — Арена (рейтинговые бои)

🎰 <b>Активности:</b>
/gacha — Крутануть гачу (бесплатно раз в 4ч)
/daily — Ежедневная награда
/quest — Квесты и задания
/dungeon — Данжеон (PvE)

🛒 <b>Магазин:</b>
/shop — Магазин предметов
/inventory — Твой инвентарь

🏆 <b>Рейтинг:</b>
/top — Топ игроков
/top_dildos — Топ дилдаков сервера

📊 <b>Прочее:</b>
/stats — Статистика бота
/help — Эта справка
"""

# ══════════════════════════════════════════════════════════════
# 🗄️ БАЗА ДАННЫХ
# ══════════════════════════════════════════════════════════════

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT DEFAULT '',
                full_name TEXT DEFAULT '',
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                gold INTEGER DEFAULT 500,
                gems INTEGER DEFAULT 10,
                hp INTEGER DEFAULT 100,
                max_hp INTEGER DEFAULT 100,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                total_damage INTEGER DEFAULT 0,
                arena_rating INTEGER DEFAULT 1000,
                equipped_dildo_id INTEGER DEFAULT 0,
                last_daily TEXT DEFAULT '',
                last_gacha TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                crit_bonus INTEGER DEFAULT 0,
                atk_bonus INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS dildos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER,
                name TEXT,
                rarity TEXT DEFAULT 'common',
                material TEXT DEFAULT '',
                level INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                base_atk INTEGER DEFAULT 10,
                base_def INTEGER DEFAULT 5,
                base_spd INTEGER DEFAULT 5,
                hp INTEGER DEFAULT 50,
                max_hp INTEGER DEFAULT 50,
                crit_chance INTEGER DEFAULT 5,
                ability_name TEXT DEFAULT '',
                ability_emoji TEXT DEFAULT '',
                ability_dmg INTEGER DEFAULT 5,
                ability_desc TEXT DEFAULT '',
                kills INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id TEXT,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS quest_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quest_id TEXT,
                progress INTEGER DEFAULT 0,
                completed INTEGER DEFAULT 0,
                claimed INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            );

            CREATE TABLE IF NOT EXISTS battle_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attacker_id INTEGER,
                defender_id INTEGER,
                winner_id INTEGER,
                battle_type TEXT DEFAULT 'pve',
                log_text TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.commit()


async def get_player(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cur:
            return await cur.fetchone()


async def create_player(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO players (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        await db.commit()


async def update_player(user_id: int, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values())
        vals.append(user_id)
        await db.execute(f"UPDATE players SET {sets} WHERE user_id = ?", vals)
        await db.commit()


async def get_player_dildos(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM dildos WHERE owner_id = ? ORDER BY base_atk DESC", (user_id,)) as cur:
            return await cur.fetchall()


async def get_dildo(dildo_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM dildos WHERE id = ?", (dildo_id,)) as cur:
            return await cur.fetchone()


async def create_dildo(owner_id: int, rarity: str = None) -> dict:
    if rarity is None:
        rarity = roll_rarity()

    r = RARITIES[rarity]
    name = random.choice(DILDO_NAMES[rarity])
    material = random.choice(MATERIALS)
    ability = random.choice(ABILITIES[rarity])

    base_atk = int(random.randint(8, 15) * r["mult"])
    base_def = int(random.randint(3, 10) * r["mult"])
    base_spd = int(random.randint(3, 10) * r["mult"])
    hp = int(random.randint(40, 70) * r["mult"])
    crit = 5 + int(r["mult"] * 2)

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO dildos 
            (owner_id, name, rarity, material, base_atk, base_def, base_spd, 
             hp, max_hp, crit_chance, ability_name, ability_emoji, ability_dmg, ability_desc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (owner_id, name, rarity, material, base_atk, base_def, base_spd,
             hp, hp, crit, ability[0], ability[1], ability[2], ability[3])
        )
        dildo_id = cursor.lastrowid
        await db.commit()

    return {
        "id": dildo_id, "name": name, "rarity": rarity, "material": material,
        "base_atk": base_atk, "base_def": base_def, "base_spd": base_spd,
        "hp": hp, "max_hp": hp, "crit_chance": crit,
        "ability_name": ability[0], "ability_emoji": ability[1],
        "ability_dmg": ability[2], "ability_desc": ability[3],
    }


async def get_inventory(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM inventory WHERE user_id = ? AND quantity > 0", (user_id,)) as cur:
            return await cur.fetchall()


async def add_item(user_id: int, item_id: str, qty: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_id = ?",
            (user_id, item_id)
        ) as cur:
            row = await cur.fetchone()
        if row:
            await db.execute("UPDATE inventory SET quantity = quantity + ? WHERE id = ?", (qty, row[0]))
        else:
            await db.execute("INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?)",
                             (user_id, item_id, qty))
        await db.commit()


async def use_item(user_id: int, item_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, quantity FROM inventory WHERE user_id = ? AND item_id = ?",
            (user_id, item_id)
        ) as cur:
            row = await cur.fetchone()
        if row and row[1] > 0:
            await db.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = ?", (row[0],))
            await db.commit()
            return True
        return False


async def get_quest_progress(user_id: int, quest_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM quest_progress WHERE user_id = ? AND quest_id = ?",
            (user_id, quest_id)
        ) as cur:
            return await cur.fetchone()


async def update_quest(user_id: int, quest_id: str, progress: int):
    async with aiosqlite.connect(DB_PATH) as db:
        existing = await get_quest_progress(user_id, quest_id)
        if existing:
            await db.execute(
                "UPDATE quest_progress SET progress = ? WHERE user_id = ? AND quest_id = ?",
                (progress, user_id, quest_id)
            )
        else:
            await db.execute(
                "INSERT INTO quest_progress (user_id, quest_id, progress) VALUES (?, ?, ?)",
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


async def count_players():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM players") as cur:
            row = await cur.fetchone()
            return row[0]


async def count_dildos():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM dildos") as cur:
            row = await cur.fetchone()
            return row[0]


# ══════════════════════════════════════════════════════════════
# 🎲 ИГРОВАЯ ЛОГИКА
# ══════════════════════════════════════════════════════════════

def roll_rarity() -> str:
    roll = random.uniform(0, 100)
    cumulative = 0
    for rarity, data in RARITIES.items():
        cumulative += data["chance"]
        if roll <= cumulative:
            return rarity
    return "common"


def exp_for_level(level: int) -> int:
    return int(100 * (level ** 1.5))


def dildo_exp_for_level(level: int) -> int:
    return int(50 * (level ** 1.3))


async def add_exp(user_id: int, amount: int) -> tuple[bool, int]:
    """Добавить опыт. Возвращает (leveled_up, new_level)"""
    player = await get_player(user_id)
    new_exp = player["exp"] + amount
    level = player["level"]
    leveled = False

    while new_exp >= exp_for_level(level):
        new_exp -= exp_for_level(level)
        level += 1
        leveled = True

    new_max_hp = 100 + (level - 1) * 15
    await update_player(user_id, exp=new_exp, level=level, max_hp=new_max_hp, hp=new_max_hp)
    return leveled, level


async def add_dildo_exp(dildo_id: int, amount: int) -> tuple[bool, int]:
    dildo = await get_dildo(dildo_id)
    if not dildo:
        return False, 0

    new_exp = dildo["exp"] + amount
    level = dildo["level"]
    leveled = False

    while new_exp >= dildo_exp_for_level(level):
        new_exp -= dildo_exp_for_level(level)
        level += 1
        leveled = True

    r = RARITIES[dildo["rarity"]]
    atk_growth = int(2 * r["mult"])
    def_growth = int(1 * r["mult"])
    hp_growth = int(5 * r["mult"])

    new_atk = dildo["base_atk"] + atk_growth * (level - dildo["level"])
    new_def = dildo["base_def"] + def_growth * (level - dildo["level"])
    new_hp = dildo["max_hp"] + hp_growth * (level - dildo["level"])

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """UPDATE dildos SET exp=?, level=?, base_atk=?, base_def=?, 
               hp=?, max_hp=? WHERE id=?""",
            (new_exp, level, new_atk, new_def, new_hp, new_hp, dildo_id)
        )
        await db.commit()

    return leveled, level


def generate_enemy(player_level: int) -> dict:
    """Генерирует ИИ-врага для PvE"""
    enemy_level = max(1, player_level + random.randint(-2, 3))
    rarity = roll_rarity()
    r = RARITIES[rarity]

    enemy_names = [
        "Безумный Вибратор", "Дикий Фаллос", "Резиновый Бандит", "Силиконовый Маньяк",
        "Призрачный Хер", "Демон Наслаждений", "Гоблин-Извращенец", "Тролль с Дилдаком",
        "Орк-Доминатор", "Суккуб Подворотни", "Скелет-Онанист", "Зомби-Эксгибиционист",
        "Дракон-Нимфоман", "Минотавр Похоти", "Ведьма с Коллекцией", "Гидра Трёхголовая",
    ]

    name = random.choice(enemy_names)
    dildo_name = random.choice(DILDO_NAMES[rarity])
    ability = random.choice(ABILITIES[rarity])

    atk = int((8 + enemy_level * 3) * r["mult"])
    defense = int((3 + enemy_level * 2) * r["mult"])
    hp = int((40 + enemy_level * 12) * r["mult"])
    crit = 5 + int(r["mult"] * 2)

    return {
        "name": name, "level": enemy_level, "rarity": rarity,
        "dildo_name": dildo_name,
        "atk": atk, "defense": defense, "hp": hp, "max_hp": hp, "crit": crit,
        "ability_name": ability[0], "ability_emoji": ability[1],
        "ability_dmg": ability[2], "ability_desc": ability[3],
    }


async def simulate_battle(player_id: int, dildo_id: int, enemy: dict) -> dict:
    """Симулирует полный бой, возвращает лог"""
    player = await get_player(player_id)
    dildo = await get_dildo(dildo_id)

    if not dildo:
        return {"error": "Нет экипированного дилдо!"}

    p_hp = dildo["max_hp"]
    e_hp = enemy["hp"]
    p_atk = dildo["base_atk"] + player["atk_bonus"]
    e_atk = enemy["atk"]
    p_def = dildo["base_def"]
    e_def = enemy["defense"]
    p_crit = dildo["crit_chance"] + player["crit_bonus"]
    e_crit = enemy["crit"]
    p_name = player["full_name"] or player["username"] or f"Игрок #{player_id}"
    e_name = enemy["name"]

    log_lines = []
    round_num = 0
    total_p_dmg = 0
    total_e_dmg = 0

    log_lines.append(f"⚔️ <b>{p_name}</b> VS <b>{e_name}</b> (Ур.{enemy['level']})")
    log_lines.append(f"🍆 «{dildo['name']}» VS 🍆 «{enemy['dildo_name']}»")
    log_lines.append(f"❤️ {p_hp} HP  ⚔️ {p_atk} ATK | ❤️ {e_hp} HP  ⚔️ {e_atk} ATK")
    log_lines.append("━" * 30)

    while p_hp > 0 and e_hp > 0 and round_num < 20:
        round_num += 1
        log_lines.append(f"\n📍 <b>Раунд {round_num}</b>")

        # === Ход игрока ===
        use_ability = random.random() < 0.3 and round_num > 1
        if use_ability:
            raw_dmg = dildo["ability_dmg"] + int(p_atk * 0.5)
            action_text = f"{dildo['ability_emoji']} <b>{dildo['ability_name']}</b>!"
        else:
            raw_dmg = p_atk + random.randint(-3, 5)
            action_text = random.choice(BATTLE_COMMENTS).format(
                attacker=p_name, defender=e_name,
                dildo=dildo["name"], action=dildo.get("ability_desc", "бьёт")
            )

        # Крит
        is_crit = random.randint(1, 100) <= p_crit
        if is_crit:
            raw_dmg = int(raw_dmg * 1.8)

        # Уворот
        dodge_chance = min(25, e_def // 2)
        is_dodge = random.randint(1, 100) <= dodge_chance

        if is_dodge:
            log_lines.append(random.choice(DODGE_COMMENTS).format(
                defender=e_name, dildo=dildo["name"]
            ))
        else:
            final_dmg = max(1, raw_dmg - e_def // 3)
            e_hp -= final_dmg
            total_p_dmg += final_dmg
            log_lines.append(f"  {action_text}")
            if is_crit:
                log_lines.append(f"  {random.choice(CRIT_COMMENTS).format(defender=e_name)}")
            log_lines.append(f"  💔 -{final_dmg} HP → {e_name}: {max(0, e_hp)} HP")

        if e_hp <= 0:
            break

        # === Ход врага ===
        use_ability_e = random.random() < 0.25
        if use_ability_e:
            raw_dmg_e = enemy["ability_dmg"] + int(e_atk * 0.5)
            action_text_e = f"{enemy['ability_emoji']} <b>{enemy['ability_name']}</b>!"
        else:
            raw_dmg_e = e_atk + random.randint(-3, 5)
            action_text_e = random.choice(BATTLE_COMMENTS).format(
                attacker=e_name, defender=p_name,
                dildo=enemy["dildo_name"], action=enemy["ability_desc"]
            )

        is_crit_e = random.randint(1, 100) <= e_crit
        if is_crit_e:
            raw_dmg_e = int(raw_dmg_e * 1.8)

        dodge_p = min(25, p_def // 2)
        is_dodge_p = random.randint(1, 100) <= dodge_p

        if is_dodge_p:
            log_lines.append(random.choice(DODGE_COMMENTS).format(
                defender=p_name, dildo=enemy["dildo_name"]
            ))
        else:
            final_dmg_e = max(1, raw_dmg_e - p_def // 3)
            p_hp -= final_dmg_e
            total_e_dmg += final_dmg_e
            log_lines.append(f"  {action_text_e}")
            if is_crit_e:
                log_lines.append(f"  {random.choice(CRIT_COMMENTS).format(defender=p_name)}")
            log_lines.append(f"  💔 -{final_dmg_e} HP → {p_name}: {max(0, p_hp)} HP")

    # === Результат ===
    log_lines.append("\n" + "═" * 30)
    won = p_hp > 0

    if won:
        gold_reward = int(30 * enemy["level"] * RARITIES[enemy["rarity"]]["mult"])
        exp_reward = int(25 * enemy["level"] * RARITIES[enemy["rarity"]]["mult"])
        dildo_exp_reward = int(15 * enemy["level"] * RARITIES[enemy["rarity"]]["mult"])

        log_lines.append(f"🏆 <b>ПОБЕДА!</b> {p_name} уничтожил {e_name}!")
        log_lines.append(f"💰 +{gold_reward} золота")
        log_lines.append(f"⭐ +{exp_reward} опыта игроку")
        log_lines.append(f"🍆 +{dildo_exp_reward} опыта дилдо")
        log_lines.append(f"📊 Нанесено урона: {total_p_dmg}")

        # Обновляем статы
        player_data = await get_player(player_id)
        await update_player(player_id,
                            gold=player_data["gold"] + gold_reward,
                            wins=player_data["wins"] + 1,
                            total_damage=player_data["total_damage"] + total_p_dmg)

        leveled, new_lvl = await add_exp(player_id, exp_reward)
        if leveled:
            log_lines.append(f"\n🎉 <b>УРОВЕНЬ ПОВЫШЕН!</b> Теперь ты {new_lvl} уровня!")

        d_leveled, d_new_lvl = await add_dildo_exp(dildo_id, dildo_exp_reward)
        if d_leveled:
            log_lines.append(f"🍆✨ Дилдо «{dildo['name']}» повысился до {d_new_lvl} уровня!")

        # Обновляем убийства дилдо
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE dildos SET kills = kills + 1 WHERE id = ?", (dildo_id,))
            await db.commit()

        # Шанс дропа
        drop_chance = 15 + int(RARITIES[enemy["rarity"]]["mult"] * 5)
        if random.randint(1, 100) <= drop_chance:
            drop = await create_dildo(player_id, enemy["rarity"])
            r = RARITIES[drop["rarity"]]
            log_lines.append(f"\n🎁 <b>ДРОП!</b> Ты получил дилдо!")
            log_lines.append(f"  {r['emoji']} «{drop['name']}» [{r['name']}]")
            log_lines.append(f"  ⚔️ {drop['base_atk']} ATK | 🛡 {drop['base_def']} DEF")

        # Квесты
        await check_quests(player_id, "wins", player_data["wins"] + 1)

    else:
        exp_consolation = int(10 * enemy["level"])
        log_lines.append(f"💀 <b>ПОРАЖЕНИЕ!</b> {e_name} оказался сильнее...")
        log_lines.append(f"⭐ +{exp_consolation} опыта утешения")
        log_lines.append(f"📊 Нанесено урона: {total_p_dmg}")

        player_data = await get_player(player_id)
        await update_player(player_id,
                            losses=player_data["losses"] + 1,
                            total_damage=player_data["total_damage"] + total_p_dmg)
        await add_exp(player_id, exp_consolation)

    return {
        "won": won,
        "log": "\n".join(log_lines),
        "rounds": round_num,
        "player_dmg": total_p_dmg,
        "enemy_dmg": total_e_dmg,
    }


async def check_quests(user_id: int, quest_type: str, current_value: int):
    for quest in QUEST_LIST:
        if quest["type"] == quest_type:
            progress = min(current_value, quest["target"])
            await update_quest(user_id, quest["id"], progress)


# ══════════════════════════════════════════════════════════════
# ⌨️ КЛАВИАТУРЫ
# ══════════════════════════════════════════════════════════════

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
            InlineKeyboardButton(text="🍆 Коллекция", callback_data="collection"),
        ],
        [
            InlineKeyboardButton(text="⚔️ В БОЙ!", callback_data="battle"),
            InlineKeyboardButton(text="🏟 Арена", callback_data="arena"),
        ],
        [
            InlineKeyboardButton(text="🎰 Гача", callback_data="gacha"),
            InlineKeyboardButton(text="🎁 Ежедневка", callback_data="daily"),
        ],
        [
            InlineKeyboardButton(text="🛒 Магазин", callback_data="shop"),
            InlineKeyboardButton(text="🎒 Инвентарь", callback_data="inventory"),
        ],
        [
            InlineKeyboardButton(text="📜 Квесты", callback_data="quests"),
            InlineKeyboardButton(text="🏆 Топ", callback_data="top"),
        ],
        [
            InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
        ],
    ])


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="menu")]
    ])


def battle_result_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚔️ Ещё бой!", callback_data="battle"),
            InlineKeyboardButton(text="🔙 Меню", callback_data="menu"),
        ]
    ])


def shop_kb() -> InlineKeyboardMarkup:
    buttons = []
    for item_id, item in SHOP_ITEMS.items():
        buttons.append([InlineKeyboardButton(
            text=f"{item['name']} — {item['price']}💰",
            callback_data=f"buy_{item_id}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def collection_kb(dildos: list, page: int = 0) -> InlineKeyboardMarkup:
    per_page = 5
    start = page * per_page
    end = start + per_page
    page_dildos = dildos[start:end]

    buttons = []
    for d in page_dildos:
        r = RARITIES[d["rarity"]]
        buttons.append([InlineKeyboardButton(
            text=f"{r['emoji']} {d['name']} Ур.{d['level']} ⚔️{d['base_atk']}",
            callback_data=f"dildo_{d['id']}"
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"col_page_{page-1}"))
    if end < len(dildos):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"col_page_{page+1}"))
    if nav:
        buttons.append(nav)

    buttons.append([InlineKeyboardButton(text="🔙 Меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def dildo_detail_kb(dildo_id: int, is_equipped: bool) -> InlineKeyboardMarkup:
    buttons = []
    if not is_equipped:
        buttons.append([InlineKeyboardButton(
            text="⚔️ Экипировать", callback_data=f"equip_{dildo_id}"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 Коллекция", callback_data="collection")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ══════════════════════════════════════════════════════════════
# 📨 ОБРАБОТЧИКИ КОМАНД
# ══════════════════════════════════════════════════════════════

@router.message(CommandStart())
async def cmd_start(message: Message):
    await init_db()
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or ""

    player = await get_player(user_id)
    if not player:
        await create_player(user_id, username, full_name)
        dildo = await create_dildo(user_id, "common")

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE players SET equipped_dildo_id = ? WHERE user_id = ?",
                             (dildo["id"], user_id))
            await db.commit()

        r = RARITIES[dildo["rarity"]]
        text = WELCOME_TEXT + f"""
🎁 <b>Твой первый дилдак:</b>
{r['emoji']} <b>«{dildo['name']}»</b>
📦 Редкость: {r['name']}
🔨 Материал: {dildo['material']}
⚔️ Атака: {dildo['base_atk']}
🛡 Защита: {dildo['base_def']}
💨 Скорость: {dildo['base_spd']}
❤️ HP: {dildo['hp']}
🎯 Крит: {dildo['crit_chance']}%
✨ Способность: {dildo['ability_emoji']} {dildo['ability_name']}

<i>Вперёд к победам, воин!</i> 🍆⚔️
"""
        await message.answer(text, reply_markup=main_menu_kb())

        # Инициализируем квесты
        for quest in QUEST_LIST:
            await update_quest(user_id, quest["id"], 0)
    else:
        await update_player(user_id, username=username, full_name=full_name)
        await message.answer(
            f"🍆 С возвращением, <b>{full_name}</b>!\n\nГотов к битвам?",
            reply_markup=main_menu_kb()
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, reply_markup=back_kb())


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    await show_profile(message, message.from_user.id)


@router.message(Command("battle"))
async def cmd_battle(message: Message):
    await do_battle(message, message.from_user.id)


@router.message(Command("collection"))
async def cmd_collection(message: Message):
    await show_collection(message, message.from_user.id)


@router.message(Command("shop"))
async def cmd_shop(message: Message):
    await show_shop(message, message.from_user.id)


@router.message(Command("daily"))
async def cmd_daily(message: Message):
    await do_daily(message, message.from_user.id)


@router.message(Command("gacha"))
async def cmd_gacha(message: Message):
    await do_gacha(message, message.from_user.id)


@router.message(Command("quest"))
async def cmd_quest(message: Message):
    await show_quests(message, message.from_user.id)


@router.message(Command("top"))
async def cmd_top(message: Message):
    await show_top(message)


@router.message(Command("inventory"))
async def cmd_inventory(message: Message):
    await show_inventory(message, message.from_user.id)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    players = await count_players()
    dildos = await count_dildos()
    await message.answer(
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Игроков: {players}\n"
        f"🍆 Дилдаков создано: {dildos}\n"
        f"🤖 Версия: 1.0 ULTIMATE\n"
        f"⚡ Движок: aiogram 3.x",
        reply_markup=back_kb()
    )


# ══════════════════════════════════════════════════════════════
# 🔘 ОБРАБОТЧИКИ КНОПОК (CALLBACKS)
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🍆 <b>БИТВА ДИЛДАКОВ</b> 🍆\n\nВыбирай действие:",
        reply_markup=main_menu_kb()
    )


@router.callback_query(F.data == "help")
async def cb_help(callback: CallbackQuery):
    await callback.message.edit_text(HELP_TEXT, reply_markup=back_kb())


@router.callback_query(F.data == "profile")
async def cb_profile(callback: CallbackQuery):
    await show_profile(callback, callback.from_user.id)


@router.callback_query(F.data == "collection")
async def cb_collection(callback: CallbackQuery):
    await show_collection(callback, callback.from_user.id)


@router.callback_query(F.data.startswith("col_page_"))
async def cb_collection_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    dildos = await get_player_dildos(callback.from_user.id)
    if not dildos:
        await callback.answer("У тебя нет дилдаков!")
        return
    player = await get_player(callback.from_user.id)
    text = "🍆 <b>ТВОЯ КОЛЛЕКЦИЯ ДИЛДАКОВ</b> 🍆\n\n"
    text += f"Всего: {len(dildos)} шт.\nНажми на дилдак для подробностей:"
    await callback.message.edit_text(text, reply_markup=collection_kb(dildos, page))


@router.callback_query(F.data.startswith("dildo_"))
async def cb_dildo_detail(callback: CallbackQuery):
    dildo_id = int(callback.data.split("_")[1])
    dildo = await get_dildo(dildo_id)
    if not dildo:
        await callback.answer("Дилдо не найден!")
        return

    player = await get_player(callback.from_user.id)
    r = RARITIES[dildo["rarity"]]
    is_equipped = player["equipped_dildo_id"] == dildo_id

    exp_needed = dildo_exp_for_level(dildo["level"])
    exp_bar_len = 10
    exp_filled = int((dildo["exp"] / max(1, exp_needed)) * exp_bar_len)
    exp_bar = "█" * exp_filled + "░" * (exp_bar_len - exp_filled)

    text = f"""
{r['emoji']} <b>«{dildo['name']}»</b> {'⚔️ ЭКИПИРОВАН' if is_equipped else ''}

📦 Редкость: {r['name']} {r['emoji']}
🔨 Материал: {dildo['material']}
📊 Уровень: {dildo['level']}
📈 Опыт: [{exp_bar}] {dildo['exp']}/{exp_needed}

⚔️ Атака: <b>{dildo['base_atk']}</b>
🛡 Защита: <b>{dildo['base_def']}</b>
💨 Скорость: <b>{dildo['base_spd']}</b>
❤️ HP: <b>{dildo['hp']}/{dildo['max_hp']}</b>
🎯 Шанс крита: <b>{dildo['crit_chance']}%</b>

✨ Способность: {dildo['ability_emoji']} <b>{dildo['ability_name']}</b>
   <i>{dildo['ability_desc']}</i> (💥 {dildo['ability_dmg']} урона)

💀 Убийств: {dildo['kills']}
📅 Получен: {dildo['created_at'][:10]}
"""
    await callback.message.edit_text(text, reply_markup=dildo_detail_kb(dildo_id, is_equipped))


@router.callback_query(F.data.startswith("equip_"))
async def cb_equip(callback: CallbackQuery):
    dildo_id = int(callback.data.split("_")[1])
    dildo = await get_dildo(dildo_id)
    if not dildo or dildo["owner_id"] != callback.from_user.id:
        await callback.answer("Это не твой дилдо! 😤")
        return

    await update_player(callback.from_user.id, equipped_dildo_id=dildo_id)
    r = RARITIES[dildo["rarity"]]
    await callback.answer(f"✅ Экипирован: {r['emoji']} «{dildo['name']}»!")
    await cb_dildo_detail(callback)


@router.callback_query(F.data == "battle")
async def cb_battle(callback: CallbackQuery):
    await do_battle(callback, callback.from_user.id)


@router.callback_query(F.data == "arena")
async def cb_arena(callback: CallbackQuery):
    await do_battle(callback, callback.from_user.id, is_arena=True)


@router.callback_query(F.data == "gacha")
async def cb_gacha(callback: CallbackQuery):
    await do_gacha(callback, callback.from_user.id)


@router.callback_query(F.data == "daily")
async def cb_daily(callback: CallbackQuery):
    await do_daily(callback, callback.from_user.id)


@router.callback_query(F.data == "shop")
async def cb_shop(callback: CallbackQuery):
    await show_shop(callback, callback.from_user.id)


@router.callback_query(F.data.startswith("buy_"))
async def cb_buy(callback: CallbackQuery):
    item_id = callback.data[4:]
    await buy_item(callback, callback.from_user.id, item_id)


@router.callback_query(F.data == "inventory")
async def cb_inventory(callback: CallbackQuery):
    await show_inventory(callback, callback.from_user.id)


@router.callback_query(F.data.startswith("use_"))
async def cb_use_item(callback: CallbackQuery):
    item_id = callback.data[4:]
    await use_item_handler(callback, callback.from_user.id, item_id)


@router.callback_query(F.data == "quests")
async def cb_quests(callback: CallbackQuery):
    await show_quests(callback, callback.from_user.id)


@router.callback_query(F.data.startswith("claim_"))
async def cb_claim_quest(callback: CallbackQuery):
    quest_id = callback.data[6:]
    await claim_quest(callback, callback.from_user.id, quest_id)


@router.callback_query(F.data == "top")
async def cb_top(callback: CallbackQuery):
    await show_top(callback)


# ══════════════════════════════════════════════════════════════
# 🎮 ОСНОВНЫЕ ФУНКЦИИ ГЕЙМПЛЕЯ
# ══════════════════════════════════════════════════════════════

async def send_or_edit(event, text: str, reply_markup=None):
    """Универсальная отправка - edit для callback, send для message"""
    try:
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(text, reply_markup=reply_markup)
        else:
            await event.answer(text, reply_markup=reply_markup)
    except Exception:
        if isinstance(event, CallbackQuery):
            await event.message.answer(text, reply_markup=reply_markup)
        else:
            await event.answer(text, reply_markup=reply_markup)


async def show_profile(event, user_id: int):
    await init_db()
    player = await get_player(user_id)
    if not player:
        await send_or_edit(event, "❌ Сначала нажми /start!")
        return

    dildo = None
    if player["equipped_dildo_id"]:
        dildo = await get_dildo(player["equipped_dildo_id"])

    dildos = await get_player_dildos(user_id)
    total_battles = player["wins"] + player["losses"]
    winrate = (player["wins"] / max(1, total_battles)) * 100

    exp_needed = exp_for_level(player["level"])
    exp_bar_len = 15
    exp_filled = int((player["exp"] / max(1, exp_needed)) * exp_bar_len)
    exp_bar = "█" * exp_filled + "░" * (exp_bar_len - exp_filled)

    # Ранг по рейтингу
    rating = player["arena_rating"]
    if rating >= 2000:
        rank = "💎 Алмаз"
    elif rating >= 1600:
        rank = "🥇 Золото"
    elif rating >= 1300:
        rank = "🥈 Серебро"
    elif rating >= 1000:
        rank = "🥉 Бронза"
    else:
        rank = "🪵 Дерево"

    text = f"""
👤 <b>ПРОФИЛЬ ВОИНА</b>

🏷 Имя: <b>{player['full_name'] or player['username'] or 'Аноним'}</b>
📊 Уровень: <b>{player['level']}</b>
📈 Опыт: [{exp_bar}] {player['exp']}/{exp_needed}

💰 Золото: <b>{player['gold']}</b>
💎 Гемы: <b>{player['gems']}</b>

⚔️ Побед: <b>{player['wins']}</b>
💀 Поражений: <b>{player['losses']}</b>
📊 Винрейт: <b>{winrate:.1f}%</b>
💥 Всего урона: <b>{player['total_damage']}</b>

🏟 Рейтинг: <b>{player['arena_rating']}</b> {rank}
🍆 Дилдаков: <b>{len(dildos)}</b>
"""
    if dildo:
        r = RARITIES[dildo["rarity"]]
        text += f"""
🗡 <b>Экипировано:</b>
  {r['emoji']} «{dildo['name']}» Ур.{dildo['level']}
  ⚔️{dildo['base_atk']} 🛡{dildo['base_def']} 💨{dildo['base_spd']} ❤️{dildo['hp']}
"""
    else:
        text += "\n⚠️ <b>Нет экипированного дилдо!</b> Используй /collection"

    await send_or_edit(event, text, reply_markup=back_kb())


async def show_collection(event, user_id: int):
    await init_db()
    dildos = await get_player_dildos(user_id)
    if not dildos:
        await send_or_edit(event, "😔 У тебя пока нет дилдаков. Нажми /start!", reply_markup=back_kb())
        return

    text = f"🍆 <b>ТВОЯ КОЛЛЕКЦИЯ ДИЛДАКОВ</b> 🍆\n\n"
    text += f"Всего: {len(dildos)} шт.\nНажми на дилдак для подробностей:"
    await send_or_edit(event, text, reply_markup=collection_kb(dildos, 0))


async def do_battle(event, user_id: int, is_arena: bool = False):
    await init_db()
    player = await get_player(user_id)
    if not player:
        await send_or_edit(event, "❌ Сначала нажми /start!")
        return

    if not player["equipped_dildo_id"]:
        await send_or_edit(event, "⚠️ У тебя нет экипированного дилдо!\nИспользуй /collection чтобы выбрать.",
                          reply_markup=back_kb())
        return

    # Показываем заставку боя
    enemy = generate_enemy(player["level"])
    r = RARITIES[enemy["rarity"]]

    intro = f"""
⚔️💥 <b>БОЙ НАЧИНАЕТСЯ!</b> 💥⚔️
{'🏟 АРЕНА' if is_arena else '🗡 PvE'}

🆚 <b>{enemy['name']}</b> (Ур.{enemy['level']})
{r['emoji']} Дилдо: «{enemy['dildo_name']}» [{r['name']}]
⚔️ ATK: {enemy['atk']} | 🛡 DEF: {enemy['defense']} | ❤️ HP: {enemy['hp']}
✨ {enemy['ability_emoji']} {enemy['ability_name']}

<i>Загружаем арену...</i> 🔄
"""
    await send_or_edit(event, intro)

    # Симулируем бой
    result = await simulate_battle(user_id, player["equipped_dildo_id"], enemy)

    if "error" in result:
        await send_or_edit(event, f"❌ {result['error']}", reply_markup=back_kb())
        return

    # Арена - обновляем рейтинг
    if is_arena:
        player = await get_player(user_id)
        if result["won"]:
            rating_change = random.randint(15, 35)
            await update_player(user_id, arena_rating=player["arena_rating"] + rating_change)
            result["log"] += f"\n🏟 Рейтинг: +{rating_change} (={player['arena_rating'] + rating_change})"
        else:
            rating_change = random.randint(10, 25)
            new_rating = max(0, player["arena_rating"] - rating_change)
            await update_player(user_id, arena_rating=new_rating)
            result["log"] += f"\n🏟 Рейтинг: -{rating_change} (={new_rating})"

    # Обрезаем лог если слишком длинный
    log_text = result["log"]
    if len(log_text) > 4000:
        log_text = log_text[:3900] + "\n\n... (бой слишком эпичный для одного сообщения)"

    await send_or_edit(event, log_text, reply_markup=battle_result_kb())


async def do_gacha(event, user_id: int):
    await init_db()
    player = await get_player(user_id)
    if not player:
        await send_or_edit(event, "❌ Сначала нажми /start!")
        return

    # Проверяем кулдаун (4 часа)
    now = datetime.now()
    if player["last_gacha"]:
        last = datetime.fromisoformat(player["last_gacha"])
        diff = now - last
        if diff < timedelta(hours=4):
            remaining = timedelta(hours=4) - diff
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            await send_or_edit(event,
                f"⏳ Гача будет доступна через <b>{hours}ч {minutes}мин</b>\n\n"
                f"Или купи 🎰 Лотерейный Билет в /shop!",
                reply_markup=back_kb())
            return

    await update_player(user_id, last_gacha=now.isoformat())

    # Крутим гачу!
    animations = ["🎰 Крутим...", "🎰 Крутим... 🍆", "🎰 Крутим... 🍆🍆", "🎰 Крутим... 🍆🍆🍆"]

    dildo = await create_dildo(user_id)
    r = RARITIES[dildo["rarity"]]

    # Дополнительные эффекты для редких
    rarity_effects = {
        "common":    "Ну... бывает и хуже.",
        "uncommon":  "Неплохо, неплохо!",
        "rare":      "О, это уже интересно! 👀",
        "epic":      "ЁБАНЫЙ В РОТ! ЭПИК! 🔥",
        "legendary": "ААААА! ЛЕГЕНДАРКА! МАМА, СМОТРИ! 🌟🌟🌟",
        "mythic":    "НЕТ БЛЯТЬ! МИФИЧЕСКИЙ?! ТЫ ИЗБРАННЫЙ! ⚡⚡⚡",
        "divine":    "Б О Ж Е С Т В Е Н Н Ы Й. Ты выиграл эту игру. 💠💠💠💠💠",
    }

    text = f"""
🎰 <b>ГАЧА ДИЛДАКОВ!</b> 🎰

🎲 Результат:
{r['emoji']} <b>«{dildo['name']}»</b>

📦 Редкость: <b>{r['name']}</b> {r['emoji']}
🔨 Материал: {dildo['material']}
⚔️ Атака: <b>{dildo['base_atk']}</b>
🛡 Защита: <b>{dildo['base_def']}</b>
💨 Скорость: <b>{dildo['base_spd']}</b>
❤️ HP: <b>{dildo['hp']}</b>
🎯 Крит: <b>{dildo['crit_chance']}%</b>
✨ {dildo['ability_emoji']} <b>{dildo['ability_name']}</b>

<i>{rarity_effects[dildo['rarity']]}</i>

⏳ Следующая бесплатная гача через 4 часа
"""
    # Обновляем квест по коллекции
    dildos = await get_player_dildos(user_id)
    await check_quests(user_id, "dildos", len(dildos))

    await send_or_edit(event, text, reply_markup=back_kb())


async def do_daily(event, user_id: int):
    await init_db()
    player = await get_player(user_id)
    if not player:
        await send_or_edit(event, "❌ Сначала нажми /start!")
        return

    now = datetime.now().date().isoformat()
    if player["last_daily"] == now:
        await send_or_edit(event,
            "⏳ Ты уже забирал ежедневную награду сегодня!\n"
            "Приходи завтра 🌅",
            reply_markup=back_kb())
        return

    # Рандомная награда
    gold_reward = random.randint(100, 300) + player["level"] * 20
    gems_reward = random.randint(1, 5)
    exp_reward = random.randint(30, 80) + player["level"] * 10

    await update_player(user_id,
                        last_daily=now,
                        gold=player["gold"] + gold_reward,
                        gems=player["gems"] + gems_reward)

    leveled, new_lvl = await add_exp(user_id, exp_reward)

    text = f"""
🎁 <b>ЕЖЕДНЕВНАЯ НАГРАДА!</b> 🎁

💰 +{gold_reward} золота
💎 +{gems_reward} гемов
⭐ +{exp_reward} опыта
"""
    if leveled:
        text += f"\n🎉 <b>УРОВЕНЬ ПОВЫШЕН!</b> Теперь ты {new_lvl} уровня!"

    # 10% шанс бонусного дилдо
    if random.random() < 0.10:
        bonus_dildo = await create_dildo(user_id)
        r = RARITIES[bonus_dildo["rarity"]]
        text += f"\n\n🎊 <b>БОНУС!</b> Тебе выпал дилдак!\n"
        text += f"{r['emoji']} «{bonus_dildo['name']}» [{r['name']}]"

    text += "\n\n<i>Приходи завтра за новой наградой!</i>"

    await send_or_edit(event, text, reply_markup=back_kb())


async def show_shop(event, user_id: int):
    await init_db()
    player = await get_player(user_id)
    if not player:
        await send_or_edit(event, "❌ Сначала нажми /start!")
        return

    text = f"""
🛒 <b>МАГАЗИН</b> 🛒

💰 Твоё золото: <b>{player['gold']}</b>
💎 Твои гемы: <b>{player['gems']}</b>

<b>Товары:</b>
"""
    for item_id, item in SHOP_ITEMS.items():
        text += f"\n{item['name']}\n  <i>{item['desc']}</i> — 💰 {item['price']}\n"

    await send_or_edit(event, text, reply_markup=shop_kb())


async def buy_item(event: CallbackQuery, user_id: int, item_id: str):
    if item_id not in SHOP_ITEMS:
        await event.answer("❌ Товар не найден!")
        return

    player = await get_player(user_id)
    item = SHOP_ITEMS[item_id]

    if player["gold"] < item["price"]:
        await event.answer(f"❌ Не хватает золота! Нужно {item['price']}, у тебя {player['gold']}", show_alert=True)
        return

    await update_player(user_id, gold=player["gold"] - item["price"])

    if item["effect"] == "gacha":
        # Мгновенная гача
        dildo = await create_dildo(user_id)
        r = RARITIES[dildo["rarity"]]
        await event.answer(f"🎰 Выпал: {r['emoji']} «{dildo['name']}»!", show_alert=True)
        dildos = await get_player_dildos(user_id)
        await check_quests(user_id, "dildos", len(dildos))
    elif item["effect"] == "heal":
        player = await get_player(user_id)
        new_hp = min(player["max_hp"], player["hp"] + item["value"])
        await update_player(user_id, hp=new_hp)
        await event.answer(f"💚 Восстановлено {item['value']} HP!", show_alert=True)
    elif item["effect"] == "full_heal":
        player = await get_player(user_id)
        await update_player(user_id, hp=player["max_hp"])
        await event.answer("💚 HP полностью восстановлено!", show_alert=True)
    elif item["effect"] == "atk_boost":
        player = await get_player(user_id)
        await update_player(user_id, atk_bonus=player["atk_bonus"] + item["value"])
        await event.answer(f"💪 +{item['value']}% к атаке навсегда!", show_alert=True)
    elif item["effect"] == "crit_boost":
        player = await get_player(user_id)
        await update_player(user_id, crit_bonus=player["crit_bonus"] + item["value"])
        await event.answer(f"🎯 +{item['value']}% к криту!", show_alert=True)
    else:
        await add_item(user_id, item_id)
        await event.answer(f"✅ Куплено: {item['name']}!", show_alert=True)

    await show_shop(event, user_id)


async def show_inventory(event, user_id: int):
    await init_db()
    items = await get_inventory(user_id)

    if not items:
        await send_or_edit(event, "🎒 Твой инвентарь пуст!\n\nЗагляни в /shop", reply_markup=back_kb())
        return

    text = "🎒 <b>ИНВЕНТАРЬ</b>\n\n"
    buttons = []
    for item in items:
        if item["item_id"] in SHOP_ITEMS:
            si = SHOP_ITEMS[item["item_id"]]
            text += f"{si['name']} x{item['quantity']}\n  <i>{si['desc']}</i>\n\n"
            buttons.append([InlineKeyboardButton(
                text=f"Использовать {si['name']}",
                callback_data=f"use_{item['item_id']}"
            )])

    buttons.append([InlineKeyboardButton(text="🔙 Меню", callback_data="menu")])
    await send_or_edit(event, text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


async def use_item_handler(event: CallbackQuery, user_id: int, item_id: str):
    used = await use_item(user_id, item_id)
    if not used:
        await event.answer("❌ У тебя нет этого предмета!", show_alert=True)
        return

    item = SHOP_ITEMS.get(item_id)
    if not item:
        await event.answer("❌ Неизвестный предмет!")
        return

    player = await get_player(user_id)

    if item["effect"] == "heal":
        new_hp = min(player["max_hp"], player["hp"] + item["value"])
        await update_player(user_id, hp=new_hp)
        await event.answer(f"💚 +{item['value']} HP! Теперь: {new_hp}/{player['max_hp']}", show_alert=True)
    elif item["effect"] == "full_heal":
        await update_player(user_id, hp=player["max_hp"])
        await event.answer(f"💚 HP восстановлено: {player['max_hp']}/{player['max_hp']}", show_alert=True)

    await show_inventory(event, user_id)


async def show_quests(event, user_id: int):
    await init_db()
    player = await get_player(user_id)
    if not player:
        await send_or_edit(event, "❌ Сначала нажми /start!")
        return

    text = "📜 <b>КВЕСТЫ И ЗАДАНИЯ</b>\n\n"
    buttons = []

    for quest in QUEST_LIST:
        progress = await get_quest_progress(user_id, quest["id"])

        if not progress:
            current = 0
            completed = False
            claimed = False
        else:
            current = progress["progress"]
            completed = current >= quest["target"]
            claimed = bool(progress["claimed"])

        if claimed:
            status = "✅"
        elif completed:
            status = "🎁"
        else:
            status = "🔄"

        bar_len = 8
        filled = int((current / max(1, quest["target"])) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)

        text += f"{status} <b>{quest['name']}</b>\n"
        text += f"   {quest['desc']}\n"
        text += f"   [{bar}] {current}/{quest['target']}\n"
        text += f"   💰 Награда: {quest['reward']} золота\n\n"

        if completed and not claimed:
            buttons.append([InlineKeyboardButton(
                text=f"🎁 Забрать: {quest['name']}",
                callback_data=f"claim_{quest['id']}"
            )])

    buttons.append([InlineKeyboardButton(text="🔙 Меню", callback_data="menu")])
    await send_or_edit(event, text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


async def claim_quest(event: CallbackQuery, user_id: int, quest_id: str):
    quest = next((q for q in QUEST_LIST if q["id"] == quest_id), None)
    if not quest:
        await event.answer("❌ Квест не найден!")
        return

    progress = await get_quest_progress(user_id, quest_id)
    if not progress or progress["progress"] < quest["target"]:
        await event.answer("❌ Квест ещё не выполнен!", show_alert=True)
        return
    if progress["claimed"]:
        await event.answer("❌ Награда уже получена!", show_alert=True)
        return

    # Выдаём награду
    player = await get_player(user_id)
    await update_player(user_id, gold=player["gold"] + quest["reward"])

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE quest_progress SET claimed = 1 WHERE user_id = ? AND quest_id = ?",
            (user_id, quest_id)
        )
        await db.commit()

    await event.answer(f"🎁 +{quest['reward']} золота за «{quest['name']}»!", show_alert=True)
    await show_quests(event, user_id)


async def show_top(event):
    await init_db()
    players = await get_top_players(10)

    if not players:
        await send_or_edit(event, "🏆 Пока нет игроков!", reply_markup=back_kb())
        return

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    text = "🏆 <b>ТОП-10 ВОИНОВ ДИЛДАКОВ</b> 🏆\n\n"

    for i, p in enumerate(players):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        name = p["full_name"] or p["username"] or f"Игрок #{p['user_id']}"
        total = p["wins"] + p["losses"]
        wr = (p["wins"] / max(1, total)) * 100

        text += f"{medal} <b>{name}</b>\n"
        text += f"   📊 Ур.{p['level']} | 🏟 {p['arena_rating']} | "
        text += f"⚔️ {p['wins']}W/{p['losses']}L ({wr:.0f}%)\n\n"

    total_players = await count_players()
    text += f"\n👥 Всего игроков: {total_players}"

    await send_or_edit(event, text, reply_markup=back_kb())


# ══════════════════════════════════════════════════════════════
# 🌐 VERCEL WEBHOOK HANDLER
# ══════════════════════════════════════════════════════════════

async def process_update(update_data: dict):
    """Обрабатывает входящий апдейт от Telegram"""
    await init_db()
    update = Update(**update_data)
    await dp.feed_update(bot, update)


async def set_webhook():
    """Устанавливает вебхук"""
    await bot.set_webhook(
        url=WEBHOOK_URL,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            update_data = json.loads(body.decode("utf-8"))
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(process_update(update_data))
            loop.close()
        except Exception as e:
            print(f"Error processing update: {e}")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        """GET запрос - устанавливаем вебхук"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(set_webhook())
            loop.close()
            response = f"✅ Webhook set to {WEBHOOK_URL}"
        except Exception as e:
            response = f"❌ Error: {e}"

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))
