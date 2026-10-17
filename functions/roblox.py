"""Roblox functions. Public APIs only, no auth."""
import json
import os
import urllib.error
import urllib.request

import ui
from i18n import t

TIMEOUT = 15
USER_AGENT = "VOID-Tools/0.4 (by anubiz1337)"


def _request(url, method="GET", payload=None):
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
        return None, f"no connection ({error.reason})"


def _ask(prompt):
    return input(ui.light("   " + prompt)).strip()


def _first(data):
    if isinstance(data, dict):
        items = data.get("data")
        if items:
            return items[0]
    return None


def _pairs(pairs):
    for label, value in pairs:
        print(ui.gray(f"   {label:<14} ") + ui.light(str(value)))


def _show_user(data):
    print()
    _pairs([
        (t("label_username"), data.get("name")),
        (t("label_display"), data.get("displayName")),
        (t("label_id"), data.get("id")),
        (t("label_created"), (data.get("created") or "")[:10]),
        (t("label_banned"), data.get("isBanned")),
    ])
    description = (data.get("description") or "").strip()
    if description:
        print(ui.gray("   " + t("label_description")) + " " + ui.light(description[:120]))


def username_to_id(username):
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


def fetch_user_info(user_id):
    status, data = _request(f"https://users.roblox.com/v1/users/{user_id}")
    if status == 200 and isinstance(data, dict):
        return data
    return None


def place_to_universe(place_id):
    status, data = _request(f"https://apis.roblox.com/universes/v1/places/{place_id}/universe")
    if status == 200 and isinstance(data, dict):
        return data.get("universeId")
    return None


def _resolve_user_id():
    raw = _ask(t("prompt_user_id_name"))
    if not raw:
        print(ui.gray("   " + t("cancelled")))
        return None
    if raw.isdigit():
        return int(raw)
    user_id = username_to_id(raw)
    if user_id is None:
        print(ui.red("   " + t("user_not_found")))
    return user_id


def _resolve_place_id():
    raw = _ask(t("prompt_place_id"))
    if not raw.isdigit():
        print(ui.gray("   " + t("number_required")))
        return None
    return int(raw)


def user_lookup():
    username = _ask(t("prompt_username"))
    if not username:
        print(ui.gray("   " + t("cancelled")))
        return
    user_id = username_to_id(username)
    if user_id is None:
        print(ui.red("   " + t("user_not_found")))
        return
    data = fetch_user_info(user_id)
    if data is None:
        print(ui.red("   " + t("fetch_failed")))
        return
    _show_user(data)


def user_by_id():
    raw = _ask(t("prompt_user_id"))
    if not raw.isdigit():
        print(ui.gray("   " + t("number_required")))
        return
    data = fetch_user_info(int(raw))
    if data is None:
        print(ui.red("   " + t("fetch_failed")))
        return
    _show_user(data)


def avatar_url():
    user_id = _resolve_user_id()
    if user_id is None:
        return
    status, data = _request(
        "https://thumbnails.roblox.com/v1/users/avatar-headshot"
        f"?userIds={user_id}&size=420x420&format=Png&isCircular=false"
    )
    thumb = _first(data) if status == 200 else None
    if not thumb:
        print(ui.red("   " + t("avatar_failed")))
        return
    print()
    print(ui.light("   " + thumb.get("imageUrl", "")))


def friends_list():
    user_id = _resolve_user_id()
    if user_id is None:
        return
    status, data = _request(f"https://friends.roblox.com/v1/users/{user_id}/friends")
    friends = data.get("data") if isinstance(data, dict) else None
    if status != 200 or friends is None:
        print(ui.red("   " + t("friends_failed")))
        return
    print(ui.gray("   " + t("friends_count").format(len(friends))))
    for friend in friends[:50]:
        print(ui.light(f"   · {friend.get('displayName')} (@{friend.get('name')})  id={friend.get('id')}"))
    if len(friends) > 50:
        print(ui.gray("   " + t("friends_truncated")))


def groups_list():
    user_id = _resolve_user_id()
    if user_id is None:
        return
    status, data = _request(f"https://groups.roblox.com/v1/users/{user_id}/groups/roles")
    entries = data.get("data") if isinstance(data, dict) else None
    if status != 200 or entries is None:
        print(ui.red("   " + t("groups_failed")))
        return
    print(ui.gray("   " + t("groups_count").format(len(entries))))
    for entry in entries[:50]:
        group = entry.get("group", {})
        role = entry.get("role", {})
        print(ui.light(f"   · {group.get('name')} - {role.get('name')}  (id={group.get('id')})"))


def game_info():
    place_id = _resolve_place_id()
    if place_id is None:
        return
    universe_id = place_to_universe(place_id)
    if universe_id is None:
        print(ui.red("   " + t("game_unresolved")))
        return
    status, data = _request(f"https://games.roblox.com/v1/games?universeIds={universe_id}")
    game = _first(data) if status == 200 else None
    if not game:
        print(ui.red("   " + t("game_failed")))
        return
    print()
    _pairs([
        (t("label_game_name"), game.get("name")),
        (t("label_creator"), (game.get("creator") or {}).get("name")),
        (t("label_playing"), game.get("playing")),
        (t("label_visits"), game.get("visits")),
        (t("label_favorites"), game.get("favoritedCount")),
        (t("label_max_players"), game.get("maxPlayers")),
    ])


def game_servers():
    place_id = _resolve_place_id()
    if place_id is None:
        return
    universe_id = place_to_universe(place_id)
    if universe_id is None:
        print(ui.red("   " + t("game_unresolved")))
        return
    status, data = _request(
        f"https://games.roblox.com/v1/games/{universe_id}/servers/Public?limit=10"
    )
    servers = data.get("data") if isinstance(data, dict) else None
    if status != 200 or servers is None:
        print(ui.red("   " + t("servers_failed")))
        return
    print(ui.gray("   " + t("servers_count").format(len(servers))))
    for server in servers:
        print(ui.light(
            f"   · {server.get('id')}  {t('servers_playing')} "
            f"{server.get('playing')}/{server.get('maxPlayers')}  ping: {server.get('ping')}"
        ))


def join_game():
    place_id = _resolve_place_id()
    if place_id is None:
        return
    link = f"roblox://experiences/start?placeId={place_id}"
    print(ui.gray("   " + t("join_opening").format(link)))
    if os.name == "nt":
        os.startfile(link)
    else:
        print(ui.red("   " + t("join_windows")))


def api_status():
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
