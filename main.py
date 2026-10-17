"""VOID — консольное меню в стиле RedTiger (белая тема).

Разделы: Info / Osint / Roblox / Utilities.
Радуга — только на github-ссылках.

Запуск:  python main.py
"""
from __future__ import annotations

import math
import sys
import time

import ui
from functions import osint, roblox, utilities

try:
    import msvcrt  # только Windows: неблокирующий ввод
except ImportError:
    msvcrt = None

FPS = 15

GITHUB_USER = "anubiz1337"
REPO_URL = f"github.com/{GITHUB_USER}/void"

DRIPS = ui.make_drip_columns()  # позиции «капель» под заголовком (разные каждый запуск)


# ---------- функции раздела Info ----------
def info_about():
    print("   VOID — заготовка консольного меню (типа RedTiger).")
    print("   Белое меню, радужный github, каркас функций под Roblox и OSINT.")
    print("   Свои функции добавляй в functions/ и подключай в SECTIONS (main.py).")


def info_author():
    print("   Автор:  by anubiz1337")
    print(f"   GitHub: github.com/{GITHUB_USER}")


def info_version():
    print("   VOID v0.2")
    print(f"   Python {sys.version.split()[0]}")


def info_links():
    print(f"   Профиль: github.com/{GITHUB_USER}")
    print(f"   Репо:    {REPO_URL}")


# ---------- описание меню ----------
SECTIONS = [
    {
        "key": "i",
        "title": "Info",
        "items": [
            ("О проекте", info_about),
            ("Автор", info_author),
            ("Версия", info_version),
            ("Ссылки", info_links),
        ],
    },
    {
        "key": "o",
        "title": "Osint",
        "items": [
            ("IP Lookup", osint.ip_lookup),
            ("Domain Info", osint.domain_info),
            ("DNS Lookup", osint.dns_lookup),
            ("Username Tracker", osint.username_tracker),
            ("URL Headers", osint.url_headers),
        ],
    },
    {
        "key": "r",
        "title": "Roblox",
        "items": [
            ("User Lookup", roblox.user_lookup),
            ("User by ID", roblox.user_by_id),
            ("Avatar URL", roblox.avatar_url),
            ("Friends List", roblox.friends_list),
            ("Groups List", roblox.groups_list),
            ("Game Info", roblox.game_info),
            ("Game Servers", roblox.game_servers),
            ("Join Game", roblox.join_game),
            ("API Status", roblox.api_status),
        ],
    },
    {
        "key": "u",
        "title": "Utilities",
        "items": [
            ("System Info", utilities.system_info),
            ("Ping Roblox", utilities.ping_roblox),
            ("Open Roblox Site", utilities.open_roblox_site),
            ("Password Generator", utilities.password_generator),
            ("Hash Text", utilities.hash_text),
            ("Base64 Enc/Dec", utilities.base64_tool),
            ("IP Generator", utilities.ip_generator),
            ("TODO Stub", utilities.todo_stub),
        ],
    },
]


# ---------- сборка кадра ----------
def _item_line(number: int, label: str, width: int = 30) -> str:
    plain = f"[{number:02d}] {label}"
    colored = ui.gray(f"[{number:02d}]") + " " + ui.light(label)
    return colored + " " * max(2, width - len(plain))


def build_screen(t: float, section_idx: int, buffer: str, message: str):
    phase = (t * 100.0) % 360
    glow = 0.86 + 0.14 * math.sin(t * 2.0)  # лёгкое «дыхание» белого заголовка
    lines = [""]

    # заголовок (белый) + капли (приглушённо-белые)
    for art in ui.TITLE:
        lines.append("   " + ui.white(art, glow))
    for row in ui.drip_rows(DRIPS, t):
        lines.append("   " + ui.white(row, 0.45))

    # github под заголовком — радужный
    lines.append("")
    lines.append("   " + ui.rainbow(f"github.com/{GITHUB_USER}", phase))
    lines.append("")

    # панель разделов
    parts = []
    visible = 0
    for index, section in enumerate(SECTIONS):
        label = f"[{section['key'].upper()}] {section['title']}"
        block = f" {label} "
        parts.append(ui.badge(block) if index == section_idx else " " + ui.light(label) + " ")
        visible += len(block)
        if index != len(SECTIONS) - 1:
            parts.append(" ")
            visible += 1
    hint = "[N] Next"
    pad = max(2, 73 - visible - len(hint))
    lines.append("   " + "".join(parts) + " " * pad + ui.gray(hint))

    # заголовок раздела
    title = SECTIONS[section_idx]["title"]
    lines.append("")
    lines.append("   " + ui.white(f"────────┤ {title} ├────────", 0.9))
    lines.append("")

    # пункты в две колонки
    items = SECTIONS[section_idx]["items"]
    half = (len(items) + 1) // 2
    for i in range(half):
        row = "   " + _item_line(i + 1, items[i][0])
        other = i + half
        if other < len(items):
            row += _item_line(other + 1, items[other][0])
        lines.append(row)

    # командная строка
    cursor = "▓" if int(t * 2) % 2 == 0 else " "
    lines.append("")
    lines.append("   " + ui.gray("─" * 60))
    lines.append("   " + ui.white("Command:") + " " + ui.light(buffer) + ui.white(cursor))
    lines.append("   " + (ui.gray("[!] ") + ui.red(message) if message else ""))

    # низ: подпись белая, ссылка на репо — радужная
    lines.append("")
    lines.append("   " + ui.white("by anubiz1337") + ui.gray("  ·  ")
                 + ui.rainbow(REPO_URL, phase + 140, hue_step=14))
    return lines


# ---------- запуск пунктов меню ----------
def run_item(label: str, func) -> None:
    sys.stdout.write(ui.SHOW_CURSOR + ui.RESET + ui.CLEAR)
    print(ui.white(f"── {label} " + "─" * 40, 0.9))
    print()
    try:
        func()
    except KeyboardInterrupt:
        print()
        print(ui.gray("   Прервано."))
    except Exception as error:  # noqa: BLE001
        print(ui.red(f"   [Ошибка] {error}"))
    print()
    try:
        input(ui.gray("   Enter — назад в меню... "))
    except (EOFError, KeyboardInterrupt):
        pass
    sys.stdout.write(ui.HIDE_CURSOR + ui.CLEAR)


# ---------- обработка команд ----------
def run_command(state: dict) -> None:
    cmd = state["buffer"].strip().lower()
    state["buffer"] = ""
    if not cmd:
        return
    if cmd in ("q", "quit", "exit", "0", "выход"):
        state["running"] = False
        return
    if cmd in ("n", "next"):
        state["section"] = (state["section"] + 1) % len(SECTIONS)
        return
    for index, section in enumerate(SECTIONS):
        if cmd == section["key"]:
            state["section"] = index
            return
    items = SECTIONS[state["section"]]["items"]
    if cmd.isdigit():
        number = int(cmd)
        if 1 <= number <= len(items):
            label, func = items[number - 1]
            run_item(label, func)
            return
    state["message"] = f"Неизвестная команда: {cmd}"


# ---------- ввод ----------
def poll_keys():
    keys = []
    if msvcrt is None:
        return keys
    while msvcrt.kbhit():
        keys.append(msvcrt.getwch())
    return keys


def handle_keys(keys, state: dict) -> None:
    i = 0
    while i < len(keys):
        ch = keys[i]
        i += 1
        if ch in ("\x00", "\xe0"):  # стрелки/функциональные клавиши: два символа
            code = keys[i] if i < len(keys) else ""
            i += 1
            if code == "M":  # вправо
                state["section"] = (state["section"] + 1) % len(SECTIONS)
            elif code == "K":  # влево
                state["section"] = (state["section"] - 1) % len(SECTIONS)
            continue
        if ch in ("\r", "\n"):
            run_command(state)
        elif ch == "\x08":
            state["buffer"] = state["buffer"][:-1]
        elif ch == "\x1b":
            state["buffer"] = ""
        elif ch == "\x03":
            state["running"] = False
        elif ch.isprintable() and len(state["buffer"]) < 40:
            state["buffer"] += ch


# ---------- режимы запуска ----------
def main() -> None:
    state = {"running": True, "section": 2, "buffer": "", "message": ""}  # старт с Roblox
    start = time.time()
    sys.stdout.write(ui.CLEAR + ui.HIDE_CURSOR)
    try:
        while state["running"]:
            t = time.time() - start
            keys = poll_keys()
            if keys:
                state["message"] = ""
                handle_keys(keys, state)
            ui.paint(build_screen(t, state["section"], state["buffer"], state["message"]))
            time.sleep(1 / FPS)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(ui.SHOW_CURSOR + ui.RESET + ui.CLEAR)
        print(ui.white("VOID") + ui.gray(" — до связи!  ") + ui.gray("by anubiz1337"))


def run_static() -> None:
    """Запасной режим без анимации (не Windows)."""
    state = {"running": True, "section": 2, "buffer": "", "message": ""}
    while state["running"]:
        ui.paint(build_screen(0.0, state["section"], state["buffer"], state["message"]))
        try:
            state["buffer"] = input("   > ")
        except (EOFError, KeyboardInterrupt):
            break
        state["message"] = ""
        run_command(state)


if __name__ == "__main__":
    ui.init_console()
    if msvcrt is None:
        run_static()
    else:
        main()
