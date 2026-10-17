"""Заготовки функций для Roblox.

Все запросы идут к публичным API Roblox (авторизация не нужна, ключи не требуются).
Список эндпоинтов: https://create.roblox.com/docs/cloud/reference

Это каркас — каждая функция уже минимально работает,
дописывай свою логику на месте пометок TODO.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

import ui

TIMEOUT = 15
USER_AGENT = "VOID-Tools/0.1 (by anubiz1337)"


# ---------- служебное ----------
def _request(url: str, method: str = "GET", payload=None):
    """Каркас HTTP-запроса к Roblox API.

    Возвращает (status, data), где data — dict/list, либо текст ошибки.
    """
    data = None
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
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


def _first(data):
    """Первый элемент из ответа вида {"data": [...]}."""
    if isinstance(data, dict):
        items = data.get("data")
        if items:
            return items[0]
    return None


def _print_pairs(pairs) -> None:
    for key, value in pairs:
        print(ui.gray(f"   {key:<14}") + ui.light(str(value)))


def _show_user(data: dict) -> None:
    print()
    _print_pairs([
        ("Username", data.get("name")),
        ("Display name", data.get("displayName")),
        ("ID", data.get("id")),
        ("Создан", (data.get("created") or "")[:10]),
        ("Забанен", data.get("isBanned")),
    ])
    description = (data.get("description") or "").strip()
    if description:
        print(ui.gray("   Описание: ") + ui.light(description[:120]))


# ---------- публичные хелперы (используй их в своих функциях) ----------
def username_to_id(username: str):
    """Username -> Roblox user id (или None)."""
    status, data = _request(
        "https://users.roblox.com/v1/usernames/users",
        method="POST",
        payload={"usernames": [username], "excludeBannedUsers": False},
    )
    if status == 200:
        user = _first(data)
        if user:
            return user.get("id")
    return None


def fetch_user_info(user_id: int):
    """User id -> словарь с данными пользователя (или None)."""
    status, data = _request(f"https://users.roblox.com/v1/users/{user_id}")
    if status == 200 and isinstance(data, dict):
        return data
    return None


def place_to_universe(place_id: int):
    """Place id -> universe id (или None)."""
    status, data = _request(f"https://apis.roblox.com/universes/v1/places/{place_id}/universe")
    if status == 200 and isinstance(data, dict):
        return data.get("universeId")
    return None


def _resolve_user_id() -> "int | None":
    """Спрашивает user id или username, возвращает числовой id."""
    raw = _ask("User ID (или username): ")
    if not raw:
        print(ui.gray("   Отменено."))
        return None
    if raw.isdigit():
        return int(raw)
    user_id = username_to_id(raw)
    if user_id is None:
        print(ui.red("   Пользователь не найден."))
    return user_id


# ---------- пункты меню ----------
def user_lookup():
    """[01] Username -> информация о пользователе."""
    username = _ask("Username: ")
    if not username:
        print(ui.gray("   Отменено."))
        return
    user_id = username_to_id(username)
    if user_id is None:
        print(ui.red("   Пользователь не найден (или нет сети)."))
        return
    data = fetch_user_info(user_id)
    if data is None:
        print(ui.red("   Не удалось получить данные."))
        return
    _show_user(data)
    # TODO: добавь сюда свои поля, например аватар или друзей


def user_by_id():
    """[02] User ID -> информация о пользователе."""
    raw = _ask("User ID: ")
    if not raw.isdigit():
        print(ui.gray("   Нужно число."))
        return
    data = fetch_user_info(int(raw))
    if data is None:
        print(ui.red("   Не удалось получить данные."))
        return
    _show_user(data)


def avatar_url():
    """[03] Ссылка на аватар пользователя."""
    user_id = _resolve_user_id()
    if user_id is None:
        return
    status, data = _request(
        "https://thumbnails.roblox.com/v1/users/avatar-headshot"
        f"?userIds={user_id}&size=420x420&format=Png&isCircular=false"
    )
    thumb = _first(data) if status == 200 else None
    if not thumb:
        print(ui.red("   Не удалось получить аватар."))
        return
    print()
    print(ui.light("   " + thumb.get("imageUrl", "")))


def friends_list():
    """[04] Список друзей пользователя."""
    user_id = _resolve_user_id()
    if user_id is None:
        return
    status, data = _request(f"https://friends.roblox.com/v1/users/{user_id}/friends")
    friends = data.get("data") if isinstance(data, dict) else None
    if status != 200 or friends is None:
        print(ui.red("   Не удалось получить список друзей."))
        return
    print(ui.gray(f"   Друзей: {len(friends)}"))
    for friend in friends[:50]:
        print(ui.light(f"   · {friend.get('displayName')} (@{friend.get('name')})  id={friend.get('id')}"))
    if len(friends) > 50:
        print(ui.gray("   ...список обрезан (первые 50)"))


def groups_list():
    """[05] Группы пользователя."""
    user_id = _resolve_user_id()
    if user_id is None:
        return
    status, data = _request(f"https://groups.roblox.com/v1/users/{user_id}/groups/roles")
    entries = data.get("data") if isinstance(data, dict) else None
    if status != 200 or entries is None:
        print(ui.red("   Не удалось получить группы."))
        return
    print(ui.gray(f"   Групп: {len(entries)}"))
    for entry in entries[:50]:
        group = entry.get("group", {})
        role = entry.get("role", {})
        print(ui.light(f"   · {group.get('name')} — {role.get('name')}  (id={group.get('id')})"))


def game_info():
    """[06] Информация об игре по Place ID."""
    raw = _ask("Place ID: ")
    if not raw.isdigit():
        print(ui.gray("   Нужно число."))
        return
    universe_id = place_to_universe(int(raw))
    if universe_id is None:
        print(ui.red("   Не удалось определить игру по этому Place ID."))
        return
    status, data = _request(f"https://games.roblox.com/v1/games?universeIds={universe_id}")
    game = _first(data) if status == 200 else None
    if not game:
        print(ui.red("   Не удалось получить данные игры."))
        return
    print()
    _print_pairs([
        ("Название", game.get("name")),
        ("Создатель", (game.get("creator") or {}).get("name")),
        ("Играют", game.get("playing")),
        ("Визитов", game.get("visits")),
        ("В избранном", game.get("favoritedCount")),
        ("Лимит игроков", game.get("maxPlayers")),
    ])


def game_servers():
    """[07] Публичные серверы игры."""
    raw = _ask("Place ID: ")
    if not raw.isdigit():
        print(ui.gray("   Нужно число."))
        return
    universe_id = place_to_universe(int(raw))
    if universe_id is None:
        print(ui.red("   Не удалось определить игру по этому Place ID."))
        return
    status, data = _request(
        f"https://games.roblox.com/v1/games/{universe_id}/servers/Public?limit=10"
    )
    servers = data.get("data") if isinstance(data, dict) else None
    if status != 200 or servers is None:
        print(ui.red("   Не удалось получить серверы."))
        return
    print(ui.gray(f"   Серверов найдено: {len(servers)}"))
    for server in servers:
        print(ui.light(
            f"   · {server.get('id')}  играют: {server.get('playing')}/{server.get('maxPlayers')}"
            f"  ping: {server.get('ping')}"
        ))


def join_game():
    """[08] Запустить Roblox и зайти в игру по Place ID (Windows)."""
    raw = _ask("Place ID: ")
    if not raw.isdigit():
        print(ui.gray("   Нужно число."))
        return
    link = f"roblox://experiences/start?placeId={int(raw)}"
    # TODO: можно добавить gameInstanceId (конкретный сервер) в ссылку
    print(ui.gray("   Открываю: ") + ui.light(link))
    if os.name == "nt":
        os.startfile(link)
    else:
        print(ui.red("   Пока поддерживается только Windows."))


def api_status():
    """[09] Проверка доступности API Roblox."""
    checks = [
        ("users.roblox.com", "https://users.roblox.com/v1/users/1"),
        ("games.roblox.com", "https://games.roblox.com/v1/games?universeIds=1"),
        ("thumbnails.roblox.com",
         "https://thumbnails.roblox.com/v1/users/avatar?userIds=1&size=150x150&format=Png"),
    ]
    for name, url in checks:
        status, _data = _request(url)
        if status == 200:
            print(ui.light("   OK    ") + ui.gray(name))
        else:
            print(ui.red("   FAIL  ") + ui.gray(f"{name} (status={status})"))
