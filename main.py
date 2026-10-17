"""VOID - terminal multi-tool menu (entry point)."""
import math
import sys
import time

import i18n
import ui
from functions import fun, osint, roblox, utilities, web
from i18n import t

try:
    import msvcrt
except ImportError:
    msvcrt = None

FPS = 20

GITHUB_USER = "anubiz1337"
REPO_URL = f"github.com/{GITHUB_USER}/void"
VERSION = "v1.0"

DRIPS = ui.make_drip_columns()


def info_about():
    print("   " + t("info_about_1"))
    print("   " + t("info_about_2"))
    print("   " + t("info_about_3"))


def info_author():
    print("   " + t("info_author_1"))
    print("   " + t("info_author_2"))


def info_version():
    print("   " + t("info_version_1"))
    print("   " + t("info_version_2").format(sys.version.split()[0]))


def info_links():
    print("   " + t("info_links_1"))
    print("   " + t("info_links_2"))


def info_language():
    i18n.toggle()
    print("   " + t("language_set"))


SECTIONS = [
    {
        "key": "i",
        "title": "sec_info",
        "items": [
            ("item_about", info_about),
            ("item_author", info_author),
            ("item_version", info_version),
            ("item_links", info_links),
            ("item_language", info_language),
        ],
    },
    {
        "key": "o",
        "title": "sec_osint",
        "items": [
            ("item_ip_lookup", osint.ip_lookup),
            ("item_domain", osint.domain_info),
            ("item_dns", osint.dns_lookup),
            ("item_subs", osint.subdomains),
            ("item_email_mx", osint.email_mx),
            ("item_username", osint.username_tracker),
            ("item_github", osint.github_lookup),
            ("item_ip_ports", osint.ip_ports),
            ("item_reverse_ip", osint.reverse_ip),
            ("item_ssl", osint.ssl_info),
            ("item_wayback", osint.wayback),
            ("item_email_sec", osint.email_security),
            ("item_ip_whois", osint.ip_whois),
        ],
    },
    {
        "key": "w",
        "title": "sec_web",
        "items": [
            ("item_url_headers", web.url_headers),
            ("item_dorks", web.dork_builder),
            ("item_expand", web.expand_url),
            ("item_portscan", web.port_scan),
            ("item_u_ping", web.ping_host),
            ("item_u_open", web.open_roblox_site),
            ("item_robots", web.robots_txt),
            ("item_siteinfo", web.site_info),
            ("item_sec_headers", web.security_headers),
        ],
    },
    {
        "key": "r",
        "title": "sec_roblox",
        "items": [
            ("item_r_lookup", roblox.user_lookup),
            ("item_r_byid", roblox.user_by_id),
            ("item_r_avatar", roblox.avatar_url),
            ("item_r_friends", roblox.friends_list),
            ("item_r_groups", roblox.groups_list),
            ("item_r_game", roblox.game_info),
            ("item_r_servers", roblox.game_servers),
            ("item_r_passes", roblox.game_passes),
            ("item_r_group", roblox.group_info),
            ("item_r_members", roblox.group_members),
            ("item_r_usergames", roblox.user_games),
            ("item_r_search", roblox.game_search),
            ("item_r_join_player", roblox.join_player),
            ("item_r_join", roblox.join_game),
            ("item_r_status", roblox.api_status),
        ],
    },
    {
        "key": "f",
        "title": "sec_fun",
        "items": [
            ("item_fun_vapor", fun.vaporwave),
            ("item_fun_leet", fun.leet_speak),
            ("item_fun_flip", fun.upside_down),
            ("item_fun_hacker", fun.hacker_id),
            ("item_fun_coin", fun.coin_flip),
            ("item_fun_game", fun.random_game),
        ],
    },
    {
        "key": "u",
        "title": "sec_utilities",
        "items": [
            ("item_u_sysinfo", utilities.system_info),
            ("item_u_pw", utilities.password_generator),
            ("item_u_hash", utilities.hash_text),
            ("item_u_b64", utilities.base64_tool),
            ("item_u_ipgen", utilities.ip_generator),
            ("item_u_db", utilities.update_databases),
            ("item_u_todo", utilities.todo_stub),
        ],
    },
]


def item_label(key):
    if key == "item_language":
        return f"{t(key)} [{i18n.LANG.upper()}]"
    return t(key)


def _item_line(number, key, elapsed, index, width=30):
    """Menu entry: white text with a quick fade-in after a section switch."""
    label = item_label(key)
    plain = f"[{number:02d}] {label}"
    progress = max(0.0, min(1.0, (elapsed - index * 0.045) / 0.28))
    alpha = 0.2 + 0.8 * (1.0 - (1.0 - progress) ** 2)
    colored = ui.white(f"[{number:02d}]", alpha * 0.8) + " " + ui.white(label, alpha)
    return colored + " " * max(2, width - len(plain))


def build_screen(ts, section_idx, buffer, message, section_ts=0.0):
    phase = (ts * 100.0) % 360
    elapsed = max(0.0, time.time() - section_ts)
    lines = [""]

    for art in ui.TITLE:
        lines.append("   " + ui.shimmer(art, ts))
    for row in ui.drip_rows(DRIPS, ts):
        lines.append("   " + "".join(
            ui.white(ch, dim) if ch != " " else " " for ch, dim in row
        ))

    lines.append("")
    link = f"github.com/{GITHUB_USER}"
    pad = max(2, 73 - len(link) - len(VERSION))
    lines.append("   " + ui.rainbow(link, phase) + " " * pad + ui.gray(VERSION))
    lines.append("")

    parts = []
    visible = 0
    for index, section in enumerate(SECTIONS):
        label = f"[{section['key'].upper()}] {t(section['title'])}"
        block = f" {label} "
        if index == section_idx:
            parts.append(" " + ui.active(label, ts) + " ")
        else:
            parts.append(" " + ui.light(label, 0.6) + " ")
        visible += len(block)
    hint = f"[N] {t('next')}"
    pad = max(2, 73 - visible - len(hint))
    lines.append("   " + "".join(parts) + " " * pad + ui.gray(hint))

    title = t(SECTIONS[section_idx]["title"])
    lines.append("")
    lines.append("   " + ui.shimmer(
        f"────────┤ {title} ├────────", ts, lo=0.7, speed=1.6, wavelength=46.0
    ))
    lines.append("")

    items = SECTIONS[section_idx]["items"]
    half = (len(items) + 1) // 2
    for i in range(half):
        row = "   " + _item_line(i + 1, items[i][0], elapsed, i)
        other = i + half
        if other < len(items):
            row += _item_line(other + 1, items[other][0], elapsed, other)
        lines.append(row)

    cursor_dim = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(ts * 4.2))
    lines.append("")
    lines.append("   " + ui.gray("─" * 60))
    lines.append("   " + ui.white(t("command")) + " " + ui.light(buffer) + ui.white("▌", cursor_dim))
    lines.append("   " + (ui.gray("[!] ") + ui.red(message) if message else ""))
    lines.append("")
    lines.append("   " + ui.white("by anubiz1337") + ui.gray("  ·  ")
                 + ui.rainbow(REPO_URL, phase + 140, hue_step=14))
    return lines


def run_item(key, func):
    sys.stdout.write(ui.SHOW_CURSOR + ui.RESET + ui.CLEAR)
    print(ui.white(f"-- {t(key)} " + "-" * 40, 0.9))
    print()
    try:
        func()
    except KeyboardInterrupt:
        print()
        print(ui.gray("   " + t("interrupted")))
    except Exception as error:
        print(ui.red(f"   [Error] {error}"))
    print()
    try:
        input(ui.gray("   " + t("back")) + " ")
    except (EOFError, KeyboardInterrupt):
        pass
    sys.stdout.write(ui.HIDE_CURSOR + ui.CLEAR)


def run_command(state):
    cmd = state["buffer"].strip().lower()
    state["buffer"] = ""
    if not cmd:
        return
    if cmd in ("q", "quit", "exit", "0"):
        state["running"] = False
        return
    if cmd in ("n", "next"):
        state["section"] = (state["section"] + 1) % len(SECTIONS)
        state["section_ts"] = time.time()
        return
    if cmd in ("l", "lang", "language"):
        i18n.toggle()
        state["message"] = t("language_set")
        return
    for index, section in enumerate(SECTIONS):
        if cmd == section["key"]:
            state["section"] = index
            state["section_ts"] = time.time()
            return
    items = SECTIONS[state["section"]]["items"]
    if cmd.isdigit():
        number = int(cmd)
        if 1 <= number <= len(items):
            run_item(items[number - 1][0], items[number - 1][1])
            return
    state["message"] = t("unknown_command").format(cmd)


def poll_keys():
    keys = []
    if msvcrt is None:
        return keys
    while msvcrt.kbhit():
        keys.append(msvcrt.getwch())
    return keys


def handle_keys(keys, state):
    i = 0
    while i < len(keys):
        ch = keys[i]
        i += 1
        if ch in ("\x00", "\xe0"):  # arrows and other special keys come in pairs
            code = keys[i] if i < len(keys) else ""
            i += 1
            if code == "M":
                state["section"] = (state["section"] + 1) % len(SECTIONS)
                state["section_ts"] = time.time()
            elif code == "K":
                state["section"] = (state["section"] - 1) % len(SECTIONS)
                state["section_ts"] = time.time()
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


def main():
    state = {
        "running": True,
        "section": 3,
        "buffer": "",
        "message": "",
        "section_ts": time.time(),
    }
    start = time.time()
    sys.stdout.write(ui.CLEAR + ui.HIDE_CURSOR)
    try:
        while state["running"]:
            ts = time.time() - start
            keys = poll_keys()
            if keys:
                state["message"] = ""
                handle_keys(keys, state)
            ui.paint(build_screen(
                ts, state["section"], state["buffer"], state["message"], state["section_ts"]
            ))
            time.sleep(1 / FPS)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(ui.SHOW_CURSOR + ui.RESET + ui.CLEAR)
        print(ui.white("VOID") + ui.gray(f" - {t('farewell')}  ") + ui.gray("by anubiz1337"))


def run_static():
    """Fallback mode without animation (non-Windows)."""
    state = {
        "running": True,
        "section": 3,
        "buffer": "",
        "message": "",
        "section_ts": 0.0,
    }
    while state["running"]:
        ui.paint(build_screen(10.0, state["section"], state["buffer"], state["message"], 0.0))
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
