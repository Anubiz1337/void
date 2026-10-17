"""Roblox functions. Public APIs only, no auth."""
import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request

import ui
from i18n import t

TIMEOUT = 15
USER_AGENT = "VOID-Tools/1.0 (by anubiz1337)"


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
        (t("label_created"), (data.get("created") or "-")[:10]),
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


def _game_icon(universe_id):
    """Icon image URL of a game."""
    status, data = _request(
        "https://thumbnails.roblox.com/v1/games/icons"
        f"?universeIds={universe_id}&size=512x512&format=Png&isCircular=false"
    )
    thumb = _first(data) if status == 200 else None
    return thumb.get("imageUrl") if thumb else None


def _game_votes(universe_id):
    """Up / down votes of a game."""
    status, data = _request(f"https://games.roblox.com/v1/games/votes?universeIds={universe_id}")
    if status == 200 and isinstance(data, dict) and data.get("data"):
        return data["data"][0]
    return None


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
    rows = [
        (t("label_game_name"), game.get("name")),
        (t("label_creator"), (game.get("creator") or {}).get("name")),
        (t("label_playing"), game.get("playing")),
        (t("label_visits"), game.get("visits")),
        (t("label_favorites"), game.get("favoritedCount")),
        (t("label_max_players"), game.get("maxPlayers")),
    ]
    votes = _game_votes(universe_id)
    if votes:
        up = votes.get("upVotes") or 0
        down = votes.get("downVotes") or 0
        total = up + down
        rows.extend([
            (t("label_up"), f"{up:,}"),
            (t("label_down"), f"{down:,}"),
            (t("label_rating"), f"{up * 100 // total}%" if total else "-"),
        ])
    print()
    _pairs(rows)
    icon = _game_icon(universe_id)
    if icon:
        print(ui.gray("   " + t("label_icon")) + " " + ui.light(icon))


def game_servers():
    place_id = _resolve_place_id()
    if place_id is None:
        return
    servers = _public_servers(place_id, 10)
    if servers is None:
        print(ui.red("   " + t("servers_failed")))
        return
    print(ui.gray("   " + t("servers_count").format(len(servers))))
    for server in servers:
        print(ui.light(
            f"   · {server.get('id')}  {t('servers_playing')} "
            f"{server.get('playing')}/{server.get('maxPlayers')}  ping: {server.get('ping')}"
        ))


def game_passes():
    """Game passes of a game with prices."""
    place_id = _resolve_place_id()
    if place_id is None:
        return
    universe_id = place_to_universe(place_id)
    if universe_id is None:
        print(ui.red("   " + t("game_unresolved")))
        return
    status, data = _request(
        f"https://apis.roblox.com/game-passes/v1/universes/{universe_id}/game-passes?limit=10"
    )
    passes = data.get("gamePasses") if isinstance(data, dict) else None
    if status != 200 or passes is None:
        print(ui.red("   " + t("fetch_failed")))
        return
    if not passes:
        print(ui.gray("   " + t("passes_none")))
        return
    print(ui.gray("   " + t("passes_count").format(len(passes))))
    for item in passes[:8]:
        info_status, info = _request(
            "https://apis.roblox.com/game-passes/v1/game-passes/"
            f"{item.get('id')}/product-info"
        )
        price = (info or {}).get("PriceInRobux") if info_status == 200 else None
        if price is not None:
            price_text = f"R$ {price}"
        elif item.get("isForSale") is False:
            price_text = t("passes_off")
        else:
            price_text = "-"
        name = str(item.get("displayName") or item.get("name") or "-")[:34]
        print(ui.light(f"   · {name}  ") + ui.gray(price_text))


def fetch_presence(user_id):
    status, data = _request(
        "https://presence.roblox.com/v1/presence/users",
        method="POST",
        payload={"userIds": [user_id]},
    )
    if status == 200 and isinstance(data, dict) and data.get("userPresences"):
        return data["userPresences"][0]
    return None


def _open_place(place_id, instance_id=None):
    link = f"roblox://experiences/start?placeId={place_id}"
    if instance_id:
        link += f"&gameInstanceId={instance_id}"
    print(ui.gray("   " + t("join_opening").format(link)))
    if os.name == "nt":
        os.startfile(link)
    else:
        print(ui.red("   " + t("join_windows")))


def _game_data(place_id):
    """Game info + universe id for a place id."""
    universe_id = place_to_universe(place_id)
    if universe_id is None:
        return None, None
    status, data = _request(f"https://games.roblox.com/v1/games?universeIds={universe_id}")
    game = _first(data) if status == 200 else None
    return game, universe_id


def _public_servers(place_id, limit=10):
    """Public server list of a place (limit must be 10, 25, 50 or 100)."""
    if limit not in (10, 25, 50, 100):
        limit = 10
    status, data = _request(
        f"https://games.roblox.com/v1/games/{place_id}/servers/Public?limit={limit}"
    )
    if status == 200 and isinstance(data, dict) and data.get("data") is not None:
        return data["data"]
    return None


def _show_servers(servers):
    print()
    print(ui.gray("   " + t("join_servers_header")))
    for index, server in enumerate(servers, 1):
        sid = str(server.get("id", ""))
        line = f"{sid[:10]}  {server.get('playing')}/{server.get('maxPlayers')}  ping {server.get('ping')}ms"
        print(ui.gray(f"   {index:02d}  ") + ui.light(line))


def _join_place_mode(place_id):
    """Show game info and its public servers, then join the chosen one."""
    game, universe_id = _game_data(place_id)
    if universe_id is None or game is None:
        print(ui.red("   " + t("game_unresolved")))
        return
    print()
    _pairs([
        (t("label_game_name"), game.get("name")),
        (t("label_playing"), game.get("playing")),
        (t("label_visits"), game.get("visits")),
    ])
    servers = _public_servers(place_id, 10)
    if not servers:
        _open_place(place_id)
        return
    _show_servers(servers)
    pick = _ask(t("prompt_pick_server"))
    if not pick:
        print(ui.gray("   " + t("cancelled")))
        return
    if pick == "0":
        _open_place(place_id)
        return
    if not pick.isdigit() or not 1 <= int(pick) <= len(servers):
        print(ui.red("   " + t("join_bad_pick")))
        return
    _open_place(place_id, servers[int(pick) - 1].get("id"))


def join_player():
    """Join by username (presence lookup) or by place id (server browser)."""
    raw = _ask(t("prompt_player_place"))
    if not raw:
        print(ui.gray("   " + t("cancelled")))
        return

    if raw.isdigit():
        _join_place_mode(int(raw))
        return

    user_id = username_to_id(raw)
    if user_id is None:
        print(ui.red("   " + t("user_not_found")))
        return

    presence = fetch_presence(user_id)
    if presence is None:
        print(ui.gray("   " + t("presence_failed")))
    elif presence.get("userPresenceType") == 2:
        place_id = presence.get("placeId") or presence.get("rootPlaceId")
        location = presence.get("lastLocation") or "-"
        print()
        print(ui.gray("   " + t("join_playing").format(location)))
        print(ui.gray("   " + t("join_place").format(place_id)))
        if _ask(t("join_confirm")).lower() in ("y", "yes", "1"):
            _open_place(place_id)
        else:
            print(ui.gray("   " + t("cancelled")))
        return
    else:
        location = presence.get("lastLocation")
        print(ui.gray("   " + t("join_not_in_game")))
        if location:
            print(ui.gray("   " + t("join_last_seen").format(location)))

    raw_place = _ask(t("join_manual_prompt"))
    if not raw_place.isdigit():
        print(ui.gray("   " + t("cancelled")))
        return
    _join_place_mode(int(raw_place))


def join_game():
    place_id = _resolve_place_id()
    if place_id is None:
        return
    _open_place(place_id)


def _resolve_group_id():
    """Group id from a number or from a name search."""
    raw = _ask(t("prompt_group"))
    if not raw:
        print(ui.gray("   " + t("cancelled")))
        return None
    if raw.isdigit():
        return int(raw)
    status, data = _request(
        "https://groups.roblox.com/v1/groups/search"
        f"?keyword={urllib.parse.quote(raw)}&limit=10"
    )
    results = data.get("data") if isinstance(data, dict) else None
    if status != 200 or not results:
        print(ui.gray("   " + t("no_results")))
        return None
    print()
    for index, group in enumerate(results, 1):
        line = f"{group.get('name')}  ({t('label_members').lower()}: {group.get('memberCount')})"
        print(ui.gray(f"   {index:02d}  ") + ui.light(line[:60]))
    pick = _ask(t("prompt_pick_number"))
    if not pick.isdigit() or not 1 <= int(pick) <= len(results):
        print(ui.gray("   " + t("cancelled")))
        return None
    return results[int(pick) - 1].get("id")


def group_info():
    """Group data by id or by name search."""
    group_id = _resolve_group_id()
    if group_id is None:
        return
    status, data = _request(f"https://groups.roblox.com/v1/groups/{group_id}")
    if status != 200 or not isinstance(data, dict):
        print(ui.red("   " + t("group_failed")))
        return
    owner = data.get("owner") or {}
    print()
    _pairs([
        (t("label_game_name"), data.get("name")),
        (t("label_id"), data.get("id")),
        (t("label_owner"), f"{owner.get('displayName')} (@{owner.get('username')})"),
        (t("label_members"), data.get("memberCount")),
        (t("label_created"), (data.get("created") or "-")[:10]),
        (t("label_public"), t("yes") if data.get("publicEntryAllowed") else t("no")),
    ])
    description = (data.get("description") or "").strip()
    if description:
        print(ui.gray("   " + t("label_description")) + " " + ui.light(description[:120]))


def group_members():
    """Public member list of a group."""
    group_id = _resolve_group_id()
    if group_id is None:
        return
    status, data = _request(
        f"https://groups.roblox.com/v1/groups/{group_id}/users?limit=10&sortOrder=Asc"
    )
    members = data.get("data") if isinstance(data, dict) else None
    if status != 200 or members is None:
        print(ui.red("   " + t("fetch_failed")))
        return
    if not members:
        print(ui.gray("   " + t("no_results")))
        return
    print(ui.gray("   " + t("members_count").format(len(members))))
    for item in members[:10]:
        user = item.get("user") or {}
        role = (item.get("role") or {}).get("name") or "-"
        print(
            ui.light(f"   · {user.get('username')}  ")
            + ui.gray(f"id {user.get('userId')}  {role}")
        )


def user_games():
    """Public games created by a user."""
    user_id = _resolve_user_id()
    if user_id is None:
        return
    status, data = _request(
        f"https://games.roblox.com/v2/users/{user_id}/games?limit=10&sortOrder=Desc"
    )
    games = data.get("data") if isinstance(data, dict) else None
    if status != 200 or games is None:
        print(ui.red("   " + t("fetch_failed")))
        return
    if not games:
        print(ui.gray("   " + t("no_results")))
        return
    print(ui.gray("   " + t("usergames_count").format(len(games))))
    for game in games[:10]:
        root = game.get("rootPlace") or {}
        visits = game.get("placeVisits", 0)
        print(
            ui.light(f"   · {game.get('name')[:38]}  ")
            + ui.gray(f"place {root.get('id')}  {t('label_visits').lower()}: {visits}")
        )


def game_search():
    """Find games by name, then show info and join the chosen one."""
    query = _ask(t("prompt_search_game"))
    if not query:
        print(ui.gray("   " + t("cancelled")))
        return
    status, data = _request(
        "https://apis.roblox.com/search-api/omni-search"
        f"?searchQuery={urllib.parse.quote(query)}&sessionId={secrets.token_hex(16)}&pageToken="
    )
    games = []
    if status == 200 and isinstance(data, dict):
        for group in data.get("searchResults", []):
            if group.get("contentGroupType") == "Game":
                games.extend(group.get("contents") or [])
    if not games:
        print(ui.gray("   " + t("no_results")))
        return
    print()
    for index, game in enumerate(games[:10], 1):
        line = (
            f"{game.get('name')[:36]}  "
            f"{t('label_playing').lower()}: {game.get('playerCount', 0)}  "
            f"by {game.get('creatorName') or '-'}"
        )
        print(ui.gray(f"   {index:02d}  ") + ui.light(line[:70]))
    pick = _ask(t("prompt_pick_number"))
    if not pick.isdigit() or not 1 <= int(pick) <= min(len(games), 10):
        print(ui.gray("   " + t("cancelled")))
        return
    place_id = games[int(pick) - 1].get("rootPlaceId")
    if not place_id:
        print(ui.red("   " + t("game_unresolved")))
        return
    _join_place_mode(place_id)


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
