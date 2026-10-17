"""Utility functions: system, network, generators, hashes, databases."""
import base64
import hashlib
import ipaddress
import platform
import secrets
import string
import sys
import time
import urllib.request
import webbrowser

import ui
from i18n import t

from . import database

USER_AGENT = "VOID-Tools/0.6 (by anubiz1337)"


def system_info():
    print(ui.gray("   " + t("sysinfo_os")) + ui.light(platform.platform()))
    print(ui.gray("   " + t("sysinfo_python")) + ui.light(sys.version.split()[0]))


def ping_host():
    host = input(ui.light("   " + t("prompt_ping_host"))).strip() or "roblox.com"
    if not host.startswith(("http://", "https://")):
        host = "https://" + host
    start = time.perf_counter()
    try:
        request = urllib.request.Request(host, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=15) as response:
            response.read(1)
        ms = (time.perf_counter() - start) * 1000
        print(ui.light("   " + t("ping_pong").format(ms)))
    except Exception as error:
        print(ui.red("   " + t("ping_fail").format(error)))


def open_roblox_site():
    webbrowser.open("https://www.roblox.com")
    print(ui.gray("   " + t("open_opened")))


def password_generator():
    raw = input(ui.light("   " + t("pw_length"))).strip()
    length = int(raw) if raw.isdigit() and int(raw) > 0 else 16

    symbols = input(ui.light("   " + t("pw_symbols"))).strip().lower()
    alphabet = string.ascii_letters + string.digits
    if symbols in ("y", "yes", "1"):
        alphabet += "!@#$%^&*()-_=+"

    password = "".join(secrets.choice(alphabet) for _ in range(length))
    print()
    print(ui.light(f"   {password}"))


def hash_text():
    text = input(ui.light("   " + t("hash_prompt")))
    data = text.encode("utf-8")
    print()
    print(ui.gray("   md5:    ") + ui.light(hashlib.md5(data).hexdigest()))
    print(ui.gray("   sha1:   ") + ui.light(hashlib.sha1(data).hexdigest()))
    print(ui.gray("   sha256: ") + ui.light(hashlib.sha256(data).hexdigest()))
    print(ui.gray("   sha512: ") + ui.light(hashlib.sha512(data).hexdigest()[:64] + "..."))


def base64_tool():
    mode = input(ui.light("   " + t("b64_mode"))).strip().lower()
    text = input(ui.light("   " + t("b64_text")))
    try:
        if mode.startswith("d"):
            result = base64.b64decode(text.encode("utf-8")).decode("utf-8", "replace")
        else:
            result = base64.b64encode(text.encode("utf-8")).decode("utf-8")
    except Exception as error:
        print(ui.red("   " + t("b64_error").format(error)))
        return
    print()
    print(ui.light(f"   {result}"))


def ip_generator():
    country = input(ui.light("   " + t("ipgen_country"))).strip().lower() or "ua"
    try:
        ranges = database.ip_ranges(country)
    except Exception as error:
        print(ui.red("   " + t("ipgen_db_failed").format(error)))
        return

    networks = []
    for cidr in ranges:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            continue
        if network.num_addresses > 2:
            networks.append(network)
    if not networks:
        print(ui.red("   " + t("ipgen_empty")))
        return

    total = sum(network.num_addresses for network in networks)
    print(ui.gray("   " + t("ipgen_stats").format(country.upper(), len(networks), total)))
    for _ in range(10):
        point = secrets.randbelow(total)
        chosen = networks[-1]
        for network in networks:
            if point < network.num_addresses:
                chosen = network
                break
            point -= network.num_addresses
        offset = 1 + secrets.randbelow(max(1, chosen.num_addresses - 2))
        ip = chosen.network_address + offset
        print(ui.light(f"   {ip}") + ui.gray(f"   {chosen}"))


def update_databases():
    print(ui.gray("   " + t("dbs_updating")))
    try:
        sites = database.sherlock_sites(force=True)
        print(ui.light("   " + t("dbs_sherlock").format(len(sites))))
    except Exception as error:
        print(ui.red("   " + t("dbs_error_named").format("Sherlock", error)))
    for country in database.ip_available() or ["ua"]:
        try:
            ranges = database.ip_ranges(country, force=True)
            print(ui.light("   " + t("dbs_ranges").format(country, len(ranges))))
        except Exception as error:
            print(ui.red("   " + t("dbs_error_named").format(country, error)))


def todo_stub():
    # 1) write your function in this file (or in roblox.py / osint.py)
    # 2) hook it into SECTIONS in main.py
    print(ui.gray("   " + t("todo_text")))
