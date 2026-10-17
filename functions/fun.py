"""Fun functions: text styles, coin flip, random game picker."""
import secrets
import time

import ui
from i18n import t

from . import roblox

LEET_MAP = str.maketrans({
    "a": "4", "b": "8", "e": "3", "g": "6", "i": "1", "l": "1", "o": "0",
    "s": "5", "t": "7", "z": "2",
    "A": "4", "B": "8", "E": "3", "G": "6", "I": "1", "L": "1", "O": "0",
    "S": "5", "T": "7", "Z": "2",
})

FLIP_MAP = {
    "a": "ɐ", "b": "q", "c": "ɔ", "d": "p", "e": "ǝ", "f": "ɟ", "g": "ƃ",
    "h": "ɥ", "i": "ᴉ", "j": "ɾ", "k": "ʞ", "l": "l", "m": "ɯ", "n": "u",
    "o": "o", "p": "d", "q": "b", "r": "ɹ", "s": "s", "t": "ʇ", "u": "n",
    "v": "ʌ", "w": "ʍ", "x": "x", "y": "ʎ", "z": "z",
    "0": "0", "1": "Ɩ", "2": "ᄅ", "3": "Ɛ", "4": "ㄣ", "5": "ϛ", "6": "9",
    "7": "ㄥ", "8": "8", "9": "6",
    ".": "˙", ",": "'", "?": "¿", "!": "¡", "'": ",", '"': "„",
    "(": ")", ")": "(", "[": "]", "]": "[", "{": "}", "}": "{",
    "<": ">", ">": "<", "_": "‾",
}

HACKER_A = [
    "shadow", "cyber", "ghost", "neon", "dark", "zero", "void", "toxin",
    "phantom", "crypto", "silent", "rogue", "vortex", "nova", "venom",
    "glitch", "hyper", "stealth", "onyx", "static",
]

HACKER_B = [
    "hunter", "wolf", "coder", "raven", "pixel", "wizard", "reaper", "ninja",
    "agent", "dragon", "spectre", "byte", "node", "fox", "soul", "echo",
    "drone", "ace", "kit", "mist",
]

GAME_KEYWORDS = [
    "simulator", "tycoon", "obby", "horror", "anime", "battle", "rpg",
    "parkour", "survival", "adventure",
]


def _ask(prompt):
    return input(ui.light("   " + prompt)).strip()


def _pick(items):
    return items[secrets.randbelow(len(items))]


def vaporwave():
    """Convert text to full-width vaporwave style."""
    text = _ask(t("prompt_text"))
    if not text:
        print(ui.gray("   " + t("cancelled")))
        return
    converted = "".join(
        chr(ord(ch) + 0xFEE0) if 33 <= ord(ch) <= 126 else ("\u3000" if ch == " " else ch)
        for ch in text
    )
    print(ui.light("   " + converted))


def leet_speak():
    """Convert text to l33t speak."""
    text = _ask(t("prompt_text"))
    if not text:
        print(ui.gray("   " + t("cancelled")))
        return
    print(ui.light("   " + text.translate(LEET_MAP)))


def upside_down():
    """Flip text upside down: ʇxǝʇ."""
    text = _ask(t("prompt_text"))
    if not text:
        print(ui.gray("   " + t("cancelled")))
        return
    print(ui.light("   " + "".join(FLIP_MAP.get(ch, ch) for ch in reversed(text))))


def hacker_id():
    """Random 'hacker' nickname generator."""
    print()
    for _ in range(3):
        adjective = _pick(HACKER_A)
        noun = _pick(HACKER_B)
        number = secrets.randbelow(10000)
        print(ui.light(f"   {adjective}_{noun}_{number:04d}"))


def _coin_art(label):
    width = 11
    return [
        "   ╔" + "═" * width + "╗",
        "   ║" + f"{label:^{width}}" + "║",
        "   ╚" + "═" * width + "╝",
    ]


def coin_flip():
    """Flip a coin with a short spin animation."""
    frames = "◐◓◑◒"
    while True:
        for index in range(8):
            print(ui.gray(f"   {frames[index % len(frames)]} {t('fun_flipping')}"), end="\r")
            time.sleep(0.08)
        label = t("fun_heads") if secrets.randbelow(2) == 0 else t("fun_tails")
        print(" " * 32, end="\r")
        print(ui.gray("   " + t("fun_coin_result").format(label)))
        for line in _coin_art(label):
            print(ui.light(line))
        if _ask(t("fun_coin_again")).lower() not in ("y", "yes", "1", "д"):
            break


def random_game():
    """Pick a random Roblox game and offer to join it."""
    keyword = _pick(GAME_KEYWORDS)
    status, data = roblox._request(
        "https://apis.roblox.com/search-api/omni-search"
        f"?searchQuery={keyword}&sessionId={secrets.token_hex(16)}&pageToken="
    )
    games = []
    if status == 200 and isinstance(data, dict):
        for group in data.get("searchResults", []):
            if group.get("contentGroupType") == "Game":
                games.extend(group.get("contents") or [])
    games = [game for game in games if game.get("rootPlaceId")]
    if not games:
        print(ui.gray("   " + t("no_results")))
        return
    game = _pick(games)
    print()
    print(ui.gray("   " + t("fun_game_pick")))
    print(ui.light("   " + str(game.get("name"))))
    print(ui.gray(f"   {t('label_playing')}: ") + ui.light(str(game.get("playerCount", 0))))
    print(ui.gray(f"   {t('label_creator')}: ") + ui.light(str(game.get("creatorName") or "-")))
    print(ui.gray("   " + t("join_place").format(game.get("rootPlaceId"))))
    if _ask(t("join_confirm")).lower() in ("y", "yes", "1", "д"):
        roblox._open_place(game.get("rootPlaceId"))
