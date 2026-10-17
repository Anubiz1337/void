"""Terminal rendering: ANSI colors, ASCII art, frame painting."""
import math
import os
import secrets
import sys

# control sequences
RESET = "\033[0m"
CLEAR = "\033[2J\033[H"
HOME = "\033[H"
CLEAR_DOWN = "\033[J"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

# palette (menu is white, color only on github links)
WHITE = (255, 255, 255)
SOFT = (235, 235, 235)
GRAY = (140, 140, 140)
DARK = (16, 16, 16)
RED = (229, 57, 53)  # errors only

TITLE = [
    "██╗   ██╗ ██████╗ ██╗██████╗ ",
    "██║   ██║██╔═══██╗██║██╔══██╗",
    "██║   ██║██║   ██║██║██║  ██║",
    "╚██╗ ██╔╝██║   ██║██║██║  ██║",
    " ╚████╔╝ ╚██████╔╝██║██████╔╝",
    "  ╚═══╝   ╚═════╝ ╚═╝╚═════╝ ",
]
TITLE_WIDTH = max(len(line) for line in TITLE)

DRIP_CHARS = "▓▒░"


def init_console():
    """Enable ANSI/VT mode and UTF-8 on Windows consoles."""
    if os.name == "nt":
        try:
            import ctypes

            k32 = ctypes.windll.kernel32
            k32.SetConsoleOutputCP(65001)
            k32.SetConsoleCP(65001)
            handle = k32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if k32.GetConsoleMode(handle, ctypes.byref(mode)):
                k32.SetConsoleMode(handle, mode.value | 0x0004)
            k32.SetConsoleTitleW("VOID")
        except Exception:
            pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def fg(color, text, dim=1.0):
    r, g, b = color
    r, g, b = int(r * dim), int(g * dim), int(b * dim)
    return f"\033[38;2;{r};{g};{b}m{text}{RESET}"


def white(text, dim=1.0):
    return fg(WHITE, text, dim)


def light(text, dim=1.0):
    return fg(SOFT, text, dim)


def gray(text, dim=1.0):
    return fg(GRAY, text, dim)


def red(text, dim=1.0):
    return fg(RED, text, dim)


def badge(text, glow=1.0):
    """Active tab: dark text on a white plate whose brightness can animate."""
    level = int(110 + 145 * max(0.0, min(1.0, glow)))
    dr, dg, db = DARK
    return f"\033[48;2;{level};{level};{level}m\033[38;2;{dr};{dg};{db}m\033[1m{text}\033[0m"


def hsv_to_rgb(h, s, v):
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


def rainbow(text, phase, hue_step=7.0, value=1.0, sat=0.95):
    """Paint each char in its own hue (phase shifts the whole gradient)."""
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


def shimmer(text, ts, lo=0.6, hi=1.0, speed=2.4, wavelength=24.0):
    """White text with a soft brightness wave running through it."""
    out = []
    k = 2 * math.pi / wavelength
    for x, ch in enumerate(text):
        if ch == " ":
            out.append(ch)
            continue
        wave = 0.5 + 0.5 * math.sin(x * k - ts * speed)
        out.append(fg(WHITE, ch, lo + (hi - lo) * wave))
    return "".join(out)


def make_drip_columns(count=9):
    cols = set()
    while len(cols) < count:
        cols.add(2 + secrets.randbelow(TITLE_WIDTH - 4))
    return sorted(cols)


def drip_rows(columns, ts):
    """Animated drips: per-character brightness, gently falling."""
    rows = []
    for row in range(len(DRIP_CHARS)):
        line = []
        for col in range(TITLE_WIDTH):
            if col not in columns:
                line.append((" ", 1.0))
                continue
            phase = col * 0.8
            length = 1.4 + 1.4 * math.sin(ts * 2.1 + phase)
            if row + 0.5 > length:
                line.append((" ", 1.0))
                continue
            wave = 0.5 + 0.5 * math.sin(ts * 3.2 - row * 1.3 + phase)
            dim = (0.9 - row * 0.22) * (0.7 + 0.3 * wave)
            line.append((DRIP_CHARS[row], max(0.15, min(1.0, dim))))
        rows.append(line)
    return rows


def paint(lines):
    """Redraw the frame without flicker: cursor home + clear each line."""
    buf = [HOME]
    for line in lines:
        buf.append(line)
        buf.append("\033[K\n")
    buf.append(CLEAR_DOWN)
    sys.stdout.write("".join(buf))
    sys.stdout.flush()
