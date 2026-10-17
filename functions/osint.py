"""OSINT-заготовки: IP, домены, DNS, username-поиск, заголовки сайтов.

Всё через публичные бесплатные сервисы (без ключей):
- ip-api.com       — информация об IP
- rdap.org         — WHOIS-данные домена
- socket (stdlib)  — DNS и реверс
"""
from __future__ import annotations

import concurrent.futures
import json
import secrets
import socket
import urllib.error
import urllib.request

import ui
from . import database

TIMEOUT = 15
USER_AGENT = "VOID-Tools/0.1 (by anubiz1337)"


# ---------- служебное ----------
def _request(url: str, method: str = "GET", payload=None):
    """HTTP-запрос -> (status, data). data — dict/list или текст ошибки."""
    data = None
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            body = response.read().decode("utf-8", "replace")
            try:
                return response.status, json.loads(body)
            except json.JSONDecodeError:
                return response.status, body
    except urllib.error.HTTPError as error:
        try:
            return error.code, json.loads(error.read().decode("utf-8", "replace"))
        except Exception:
            return error.code, None
    except urllib.error.URLError as error:
        return None, f"нет соединения ({error.reason})"


def _ask(prompt: str) -> str:
    return input(ui.light(f"   {prompt}")).strip()


def _pairs(pairs) -> None:
    for key, value in pairs:
        print(ui.gray(f"   {key:<14}") + ui.light(str(value)))


def _clean_domain(raw: str) -> str:
    raw = raw.strip().lower()
    for prefix in ("https://", "http://"):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
    return raw.split("/")[0]


# ---------- пункты меню ----------
def ip_lookup():
    """[01] Информация об IP-адресе (Enter = свой IP)."""
    ip = _ask("IP (Enter = твой): ")
    fields = "status,message,country,regionName,city,lat,lon,timezone,isp,org,as,query"
    url = f"http://ip-api.com/json/{ip}?fields={fields}"
    status, data = _request(url)
    if status != 200 or not isinstance(data, dict) or data.get("status") != "success":
        reason = data.get("message") if isinstance(data, dict) else status
        print(ui.red(f"   Не удалось: {reason}"))
        return
    print()
    _pairs([
        ("IP", data.get("query")),
        ("Страна", data.get("country")),
        ("Регион", data.get("regionName")),
        ("Город", data.get("city")),
        ("Координаты", f"{data.get('lat')}, {data.get('lon')}"),
        ("Таймзона", data.get("timezone")),
        ("Провайдер", data.get("isp")),
        ("Организация", data.get("org")),
        ("AS", data.get("as")),
    ])
    # TODO: добавь открытие карты по координатам или сохранение в файл


def domain_info():
    """[02] WHOIS-инфо о домене (RDAP)."""
    domain = _clean_domain(_ask("Домен (example.com): "))
    if not domain:
        print(ui.gray("   Отменено."))
        return
    status, data = _request(f"https://rdap.org/domain/{domain}")
    if status != 200 or not isinstance(data, dict):
        print(ui.red("   Не удалось получить данные домена."))
        return

    events = {event.get("eventAction"): event.get("eventDate") for event in data.get("events", [])}
    nameservers = ", ".join(ns.get("ldhName", "") for ns in data.get("nameservers", [])) or "—"

    registrar = "—"
    for entity in data.get("entities", []):
        if "registrar" in (entity.get("roles") or []):
            for prop in (entity.get("vcardArray") or [None, []])[1]:
                if prop and prop[0] == "fn":
                    registrar = prop[3]
                    break
            break

    print()
    _pairs([
        ("Домен", data.get("ldhName") or domain),
        ("Регистратор", registrar),
        ("Создан", (events.get("registration") or "—")[:10]),
        ("Истекает", (events.get("expiration") or "—")[:10]),
        ("Обновлён", (events.get("last changed") or "—")[:10]),
        ("Статус", ", ".join((data.get("status") or [])[:3]) or "—"),
        ("NS", nameservers[:70]),
    ])


def dns_lookup():
    """[03] DNS: домен -> IP, плюс реверс (PTR)."""
    host = _ask("Хост (example.com): ")
    if not host:
        print(ui.gray("   Отменено."))
        return
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as error:
        print(ui.red(f"   Не удалось разрешить: {error}"))
        return
    v4 = sorted({item[4][0] for item in infos if item[0] == socket.AF_INET})
    v6 = sorted({item[4][0] for item in infos if item[0] == socket.AF_INET6})
    print(ui.gray("   IPv4: ") + ui.light(", ".join(v4) or "—"))
    print(ui.gray("   IPv6: ") + ui.light(", ".join(v6) or "—"))

    ip = _ask("Реверс-DNS для IP (Enter = пропустить): ")
    if ip:
        try:
            name, _aliases, _addrs = socket.gethostbyaddr(ip)
            print(ui.gray("   PTR:  ") + ui.light(name))
        except (socket.herror, socket.gaierror):
            print(ui.red("   PTR не найден."))


def _check_url(url: str, timeout: float = TIMEOUT):
    """HTTP-статус страницы (200/404/…), None при ошибке сети."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except urllib.error.URLError:
        return None


def username_tracker():
    """[04] Поиск username по базе сайтов Sherlock (+ Roblox API)."""
    username = _ask("Username: ")
    if not username:
        print(ui.gray("   Отменено."))
        return

    # сайты берём из локальной базы Sherlock (~400 сайтов)
    pool = []
    try:
        sites = database.sherlock_sites()
        for name, info in sites.items():
            if not isinstance(info, dict) or info.get("isNSFW"):
                continue
            if info.get("errorType") != "status_code":
                continue
            pattern = info.get("urlProbe") or info.get("url") or ""
            if "{}" not in pattern:
                continue
            pool.append((name, pattern.replace("{}", username), info.get("errorMsg")))
    except Exception as error:  # noqa: BLE001
        print(ui.red(f"   База Sherlock недоступна: {error}"))

    # базовые сайты проверяем всегда + случайная выборка из базы
    base = [
        ("GitHub", f"https://github.com/{username}", 404),
        ("Reddit", f"https://www.reddit.com/user/{username}", 404),
        ("Twitch", f"https://www.twitch.tv/{username}", 404),
    ]
    sample = []
    remaining = list(pool)
    while remaining and len(sample) < 40:
        sample.append(remaining.pop(secrets.randbelow(len(remaining))))
    checks = base + sample
    print(ui.gray(f"   Проверяю {len(checks)} сайтов…"))

    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = {
            executor.submit(_check_url, url, 8): (name, url, error)
            for name, url, error in checks
        }
        for future in concurrent.futures.as_completed(futures):
            name, url, error = futures[future]
            code = future.result()
            if code is None:
                continue
            errors = error if isinstance(error, list) else [error]
            if code == 200 and code not in errors:
                found.append((name, url))

    # Roblox — через API, точный результат
    status, data = _request(
        "https://users.roblox.com/v1/usernames/users",
        method="POST",
        payload={"usernames": [username], "excludeBannedUsers": False},
    )
    roblox_line = None
    if status == 200 and isinstance(data, dict) and data.get("data"):
        user = data["data"][0]
        roblox_line = f"Roblox         id={user.get('id')}"

    print()
    for name, url in sorted(found):
        print(ui.light("   НАЙДЕН  ") + ui.gray(f"{name:<14} {url}"))
    if roblox_line:
        print(ui.light("   НАЙДЕН  ") + ui.gray(roblox_line))
    total_found = len(found) + (1 if roblox_line else 0)
    print(ui.gray(f"   Итог: найден на {total_found} из {len(checks) + 1} сайтов"))


def url_headers():
    """[05] Заголовки ответа сайта."""
    url = _ask("URL: ")
    if not url:
        print(ui.gray("   Отменено."))
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            print(ui.gray(f"   Статус: {response.status}"))
            for header, value in list(response.headers.items())[:12]:
                print(ui.gray(f"   {header:<22}") + ui.light(value[:80]))
    except urllib.error.HTTPError as error:
        print(ui.red(f"   HTTP {error.code}"))
    except urllib.error.URLError as error:
        print(ui.red(f"   Недоступно: {error.reason}"))
