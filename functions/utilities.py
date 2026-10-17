"""Утилиты VOID: система, сеть, генераторы, хеши, base64, базы данных.

Каждая функция — пример того, как добавлять свои пункты в меню.
Без модуля random: только криптостойкий secrets + реальные базы данных.
"""
from __future__ import annotations

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
from . import database


def system_info():
    """[01] Базовая информация о системе."""
    print(ui.gray("   OS:      ") + ui.light(platform.platform()))
    print(ui.gray("   Python:  ") + ui.light(sys.version.split()[0]))
    # TODO: добавь сюда CPU, RAM, GPU и т.д.


def ping_roblox():
    """[02] Замер задержки до roblox.com."""
    start = time.perf_counter()
    try:
        request = urllib.request.Request(
            "https://www.roblox.com",
            headers={"User-Agent": "VOID-Tools/0.3 (by anubiz1337)"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            response.read(1)
        ms = (time.perf_counter() - start) * 1000
        print(ui.light(f"   Pong! {ms:.0f} ms"))
    except Exception as error:  # noqa: BLE001
        print(ui.red(f"   Недоступно: {error}"))


def open_roblox_site():
    """[03] Открыть roblox.com в браузере."""
    webbrowser.open("https://www.roblox.com")
    print(ui.gray("   Открыл roblox.com в браузере."))


def password_generator():
    """[04] Генератор пароля (криптостойкий, secrets)."""
    raw = input(ui.light("   Длина (Enter = 16): ")).strip()
    length = int(raw) if raw.isdigit() and int(raw) > 0 else 16

    symbols = input(ui.light("   С символами (!@#…)? (y/n): ")).strip().lower()
    alphabet = string.ascii_letters + string.digits
    if symbols in ("y", "yes", "д", "да", "1"):
        alphabet += "!@#$%^&*()-_=+"

    password = "".join(secrets.choice(alphabet) for _ in range(length))
    print()
    print(ui.light(f"   {password}"))
    # TODO: добавь опцию «сохранить в файл»


def hash_text():
    """[05] Хеши текста: md5 / sha1 / sha256 / sha512."""
    text = input(ui.light("   Текст: "))
    data = text.encode("utf-8")
    print()
    print(ui.gray("   md5:    ") + ui.light(hashlib.md5(data).hexdigest()))
    print(ui.gray("   sha1:   ") + ui.light(hashlib.sha1(data).hexdigest()))
    print(ui.gray("   sha256: ") + ui.light(hashlib.sha256(data).hexdigest()))
    print(ui.gray("   sha512: ") + ui.light(hashlib.sha512(data).hexdigest()[:64] + "…"))


def base64_tool():
    """[06] Base64: кодирование/декодирование."""
    mode = input(ui.light("   [E]ncode или [D]ecode: ")).strip().lower()
    text = input(ui.light("   Текст: "))
    try:
        if mode.startswith("d"):
            result = base64.b64decode(text.encode("utf-8")).decode("utf-8", "replace")
        else:
            result = base64.b64encode(text.encode("utf-8")).decode("utf-8")
    except Exception as error:  # noqa: BLE001
        print(ui.red(f"   Ошибка: {error}"))
        return
    print()
    print(ui.light(f"   {result}"))


def ip_generator():
    """[07] IP из реальных диапазонов стран (база ipdeny.com)."""
    country = input(ui.light("   Код страны (ua/us/de…, Enter = ua): ")).strip().lower() or "ua"
    try:
        ranges = database.ip_ranges(country)
    except Exception as error:  # noqa: BLE001
        print(ui.red(f"   Не удалось получить базу: {error}"))
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
        print(ui.red("   База пустая."))
        return

    total = sum(network.num_addresses for network in networks)
    print(ui.gray(f"   Страна {country.upper()}: {len(networks)} диапазонов, {total:,} адресов"))
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
    """[08] Обновить локальные базы (sherlock + ipdeny)."""
    print(ui.gray("   Обновляю базы…"))
    try:
        sites = database.sherlock_sites(force=True)
        print(ui.light(f"   Sherlock:  {len(sites)} сайтов"))
    except Exception as error:  # noqa: BLE001
        print(ui.red(f"   Sherlock:  ошибка — {error}"))
    for country in database.ip_available() or ["ua"]:
        try:
            ranges = database.ip_ranges(country, force=True)
            print(ui.light(f"   {country}: {len(ranges)} диапазонов"))
        except Exception as error:  # noqa: BLE001
            print(ui.red(f"   {country}: ошибка — {error}"))


def todo_stub():
    """[09] Пустая заготовка — скопируй и впиши свою логику."""
    # TODO: здесь твой код.
    # 1) напиши функцию в этом файле (или functions/roblox.py / osint.py)
    # 2) подключи её в main.py -> SECTIONS
    print(ui.gray("   TODO: впиши свою функцию здесь."))
