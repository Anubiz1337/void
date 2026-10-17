"""VOID — утилиты отрисовки: ANSI-цвета, ASCII-арт, радуга, рендер кадра."""
from __future__ import annotations

import math
import os
import secrets
import sys

# ---------- управляющие последовательности ----------
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"
HOME = "\033[H"
CLEAR_DOWN = "\033[J"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

# ---------- палитра (меню — белое) ----------
WHITE = (255, 255, 255)
SOFT = (235, 235, 235)
GRAY = (140, 140, 140)
DARK = (16, 16, 16)
RED = (229, 57, 53)  # только для сообщений об ошибках

# ---------- ASCII-арт заголовка ----------
TITLE = [
    "██╗   ██╗ ██████╗ ██╗██████╗ ",
    "██║   ██║██╔═══██╗██║██╔══██╗",
    "██║   ██║██║   ██║██║██║  ██║",
    "╚██╗ ██╔╝██║   ██║██║██║  ██║",
    " ╚████╔╝ ╚██████╔╝██║██████╔╝",
    "  ╚═══╝   ╚═════╝ ╚═╝╚═════╝ ",
]
TITLE_WIDTH = max(len(line) for line in TITLE)

DRIP_LEVELS = "▓▒░"  # «капли» под заголовком


# ---------- инициализация консоли ----------
def init_console() -> None:
    """Включает VT-режим (ANSI) и UTF-8 в консоли Windows."""
    if os.name == "nt":
        try:
            import ctypes

            k32 = ctypes.windll.kernel32
            k32.SetConsoleOutputCP(65001)
            k32.SetConsoleCP(65001)
            handle = k32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if k32.GetConsoleMode(handle, ctypes.byref(mode)):
                k32.SetConsoleMode(handle, mode.value | 0x0004)  # VT processing
            k32.SetConsoleTitleW("VOID")
        except Exception:
            pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ---------- цвета ----------
def fg(color, text, dim: float = 1.0) -> str:
    r, g, b = color
    r, g, b = int(r * dim), int(g * dim), int(b * dim)
    return f"\033[38;2;{r};{g};{b}m{text}{RESET}"


def white(text, dim: float = 1.0) -> str:
    return fg(WHITE, text, dim)


def light(text, dim: float = 1.0) -> str:
    return fg(SOFT, text, dim)


def gray(text, dim: float = 1.0) -> str:
    return fg(GRAY, text, dim)


def red(text, dim: float = 1.0) -> str:
    return fg(RED, text, dim)


def badge(text) -> str:
    """Активная вкладка: чёрный текст на белой плашке."""
    wr, wg, wb = WHITE
    dr, dg, db = DARK
    return f"\033[48;2;{wr};{wg};{wb}m\033[38;2;{dr};{dg};{db}m\033[1m{text}\033[0m"


def hsv_to_rgb(h: float, s: float, v: float):
    """HSV -> RGB (0-255). h в градусах 0-360."""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)


def rainbow(text: str, phase: float, hue_step: float = 7.0, value: float = 1.0, sat: float = 0.95) -> str:
    """Красит каждый символ в свой оттенок радуги (phase — сдвиг в градусах)."""
    out = []
    for x, ch in enumerate(text):
        if ch == " ":
            out.append(ch)
            continue
        h = (phase + x * hue_step) % 360
        r, g, b = hsv_to_rgb(h, sat, value)
        out.append(f"\033[38;2;{r};{g};{b}m{ch}")
    out.append(RESET)
    return "".join(out)


# ---------- «капли» под заголовком ----------
def make_drip_columns(count: int = 9):
    cols = set()
    while len(cols) < count:
        cols.add(2 + secrets.randbelow(TITLE_WIDTH - 4))
    return sorted(cols)


def drip_rows(columns, t: float):
    """Анимированные капли: длина «стекания» плавно пульсирует."""
    rows = [[" "] * TITLE_WIDTH for _ in range(len(DRIP_LEVELS))]
    for c in columns:
        length = 1 + int((1 + math.sin(t * 2.4 + c * 1.9)) / 2 * (len(DRIP_LEVELS) - 0.01))
        for r in range(length):
            rows[r][c] = DRIP_LEVELS[r]
    return ["".join(row) for row in rows]


# ---------- рендер ----------
def paint(lines) -> None:
    """Перерисовывает экран без мерцания (курсор в начало + затирание строк)."""
    buf = [HOME]
    for line in lines:
        buf.append(line)
        buf.append("\033[K\n")
    buf.append(CLEAR_DOWN)
    sys.stdout.write("".join(buf))
    sys.stdout.flush()
