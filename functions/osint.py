"""OSINT functions: IP, domains, DNS, email MX, username search, dorks."""
import concurrent.futures
import json
import secrets
import socket
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

import ui
from i18n import t

from . import database

TIMEOUT = 15
USER_AGENT = "VOID-Tools/0.7 (by anubiz1337)"

DORK_PATTERNS = [
    "site:{}",
    "site:{} inurl:admin",
    "site:{} inurl:login",
    "site:{} filetype:pdf",
    'site:{} intitle:"index of"',
]

ENGINES = {
    "g": "https://www.google.com/search?q=",
    "b": "https://www.bing.com/search?q=",
    "d": "https://duckduckgo.com/?q=",
}


def _request(url, method="GET", payload=None, timeout=TIMEOUT):
    data = None
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
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


def _pairs(pairs):
    for label, value in pairs:
        print(ui.gray(f"   {label:<14} ") + ui.light(str(value)))


def _clean_domain(raw):
    raw = raw.strip().lower()
    for prefix in ("https://", "http://"):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
    return raw.split("/")[0]


def ip_lookup():
    ip = _ask(t("prompt_ip"))
    fields = "status,message,country,regionName,city,lat,lon,timezone,isp,org,as,query,proxy,hosting,mobile"
    status, data = _request(f"http://ip-api.com/json/{ip}?fields={fields}")
    if status != 200 or not isinstance(data, dict) or data.get("status") != "success":
        reason = data.get("message") if isinstance(data, dict) else status
        print(ui.red("   " + t("ip_failed").format(reason)))
        return
    print()
    _pairs([
        (t("label_ip"), data.get("query")),
        (t("label_country"), data.get("country")),
        (t("label_region"), data.get("regionName")),
        (t("label_city"), data.get("city")),
        (t("label_coords"), f"{data.get('lat')}, {data.get('lon')}"),
        (t("label_timezone"), data.get("timezone")),
        (t("label_isp"), data.get("isp")),
        (t("label_org"), data.get("org")),
        (t("label_as"), data.get("as")),
        (t("label_proxy"), t("yes") if data.get("proxy") else t("no")),
        (t("label_hosting"), t("yes") if data.get("hosting") else t("no")),
        (t("label_mobile"), t("yes") if data.get("mobile") else t("no")),
    ])


def domain_info():
    domain = _clean_domain(_ask(t("prompt_domain")))
    if not domain:
        print(ui.gray("   " + t("cancelled")))
        return
    status, data = _request(f"https://rdap.org/domain/{domain}")
    if status != 200 or not isinstance(data, dict):
        print(ui.red("   " + t("domain_failed")))
        return

    events = {event.get("eventAction"): event.get("eventDate") for event in data.get("events", [])}
    nameservers = ", ".join(ns.get("ldhName", "") for ns in data.get("nameservers", [])) or "-"

    registrar = "-"
    for entity in data.get("entities", []):
        if "registrar" in (entity.get("roles") or []):
            for prop in (entity.get("vcardArray") or [None, []])[1]:
                if prop and prop[0] == "fn":
                    registrar = prop[3]
                    break
            break

    print()
    _pairs([
        (t("label_domain"), data.get("ldhName") or domain),
        (t("label_registrar"), registrar),
        (t("label_created"), (events.get("registration") or "-")[:10]),
        (t("label_expires"), (events.get("expiration") or "-")[:10]),
        (t("label_updated"), (events.get("last changed") or "-")[:10]),
        (t("label_status"), ", ".join((data.get("status") or [])[:3]) or "-"),
        (t("label_ns"), nameservers[:70]),
    ])


def dns_lookup():
    host = _ask(t("prompt_host"))
    if not host:
        print(ui.gray("   " + t("cancelled")))
        return
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as error:
        print(ui.red("   " + t("dns_failed").format(error)))
        return
    v4 = sorted({item[4][0] for item in infos if item[0] == socket.AF_INET})
    v6 = sorted({item[4][0] for item in infos if item[0] == socket.AF_INET6})
    print(ui.gray("   " + t("dns_ipv4")) + ui.light(", ".join(v4) or "-"))
    print(ui.gray("   " + t("dns_ipv6")) + ui.light(", ".join(v6) or "-"))

    ip = _ask(t("prompt_reverse"))
    if ip:
        try:
            name, _aliases, _addrs = socket.gethostbyaddr(ip)
            print(ui.gray("   PTR:  ") + ui.light(name))
        except (socket.herror, socket.gaierror):
            print(ui.red("   " + t("dns_ptr_missing")))


def _crtsh_subdomains(domain):
    status, data = _request(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=45)
    if status != 200 or not isinstance(data, list):
        return None
    names = set()
    for entry in data:
        for name in str(entry.get("name_value", "")).splitlines():
            name = name.strip().lower().lstrip("*.").rstrip(".")
            if (
                name
                and name.endswith("." + domain)
                and " " not in name
                and "@" not in name
            ):
                names.add(name)
    return names


def _hostsearch_subdomains(domain):
    status, data = _request(f"https://api.hackertarget.com/hostsearch/?q={domain}", timeout=30)
    if status != 200 or not isinstance(data, str):
        return None
    names = set()
    for line in data.splitlines():
        name = line.split(",")[0].strip().lower()
        if name and name.endswith("." + domain) and " " not in name:
            names.add(name)
    return names


def subdomains():
    """Subdomain list from certificate transparency (crt.sh + hostsearch fallback)."""
    domain = _clean_domain(_ask(t("prompt_domain")))
    if not domain:
        print(ui.gray("   " + t("cancelled")))
        return
    names = _crtsh_subdomains(domain)
    if names is None:
        names = _crtsh_subdomains(domain)  # crt.sh throws 502 sometimes
    if names is None:
        names = _hostsearch_subdomains(domain)
    if names is None:
        print(ui.red("   " + t("subs_failed")))
        return
    if not names:
        print(ui.gray("   " + t("subs_none")))
        return
    print(ui.gray("   " + t("subs_count").format(len(names))))
    for name in sorted(names)[:50]:
        print(ui.light(f"   · {name}"))
    if len(names) > 50:
        print(ui.gray("   " + t("subs_truncated")))


def _mx_records(domain):
    """MX records via Cloudflare DNS-over-HTTPS (JSON)."""
    url = f"https://cloudflare-dns.com/dns-query?name={domain}&type=MX"
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/dns-json"}
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        data = json.loads(response.read().decode("utf-8", "replace"))
    return [answer.get("data", "") for answer in data.get("Answer", []) if answer.get("type") == 15]


def email_mx():
    raw = _ask(t("prompt_email"))
    if not raw:
        print(ui.gray("   " + t("cancelled")))
        return
    domain = raw.split("@")[-1].strip().lower()
    try:
        records = _mx_records(domain)
    except Exception:
        print(ui.red("   " + t("mx_failed")))
        return
    if not records:
        print(ui.gray("   " + t("mx_none")))
        return
    print(ui.gray("   " + t("mx_records")))
    for record in records:
        print(ui.light(f"   · {record}"))


def _check_url(url, timeout=TIMEOUT):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except urllib.error.URLError:
        return None


def username_tracker():
    username = _ask(t("prompt_username"))
    if not username:
        print(ui.gray("   " + t("cancelled")))
        return

    # site list comes from the local Sherlock database
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
    except Exception as error:
        print(ui.red("   " + t("tracker_db_failed").format(error)))

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
    print(ui.gray("   " + t("tracker_checking").format(len(checks))))

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

    # Roblox via the public API (exact result)
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
        print(ui.light(f"   {t('tracker_found'):<7} ") + ui.gray(f"{name:<14} {url}"))
    if roblox_line:
        print(ui.light(f"   {t('tracker_found'):<7} ") + ui.gray(roblox_line))
    total_found = len(found) + (1 if roblox_line else 0)
    print(ui.gray("   " + t("tracker_summary").format(total_found, len(checks) + 1)))


def github_lookup():
    """Public GitHub profile data by username."""
    username = _ask(t("prompt_username"))
    if not username:
        print(ui.gray("   " + t("cancelled")))
        return
    status, data = _request(f"https://api.github.com/users/{username}")
    if status == 404:
        print(ui.red("   " + t("user_not_found")))
        return
    if status != 200 or not isinstance(data, dict):
        print(ui.red("   " + t("fetch_failed")))
        return
    print()
    rows = [
        (t("label_username"), data.get("login")),
        (t("label_name"), data.get("name")),
        (t("label_bio"), data.get("bio")),
        (t("label_company"), data.get("company")),
        (t("label_location"), data.get("location")),
        (t("label_blog"), data.get("blog")),
        (t("label_twitter"), data.get("twitter_username")),
        (t("label_repos"), data.get("public_repos")),
        (t("label_followers"), data.get("followers")),
        (t("label_created"), (data.get("created_at") or "")[:10]),
    ]
    _pairs([(label, value) for label, value in rows if value not in (None, "")])


def url_headers():
    url = _ask(t("prompt_url"))
    if not url:
        print(ui.gray("   " + t("cancelled")))
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            print(ui.gray("   " + t("headers_status").format(response.status)))
            for header, value in list(response.headers.items())[:12]:
                print(ui.gray(f"   {header:<22}") + ui.light(value[:80]))
    except urllib.error.HTTPError as error:
        print(ui.red("   " + t("headers_http").format(error.code)))
    except urllib.error.URLError as error:
        print(ui.red("   " + t("headers_unreachable").format(error.reason)))


def dork_builder():
    target = _ask(t("prompt_target"))
    if not target:
        print(ui.gray("   " + t("cancelled")))
        return
    engine = _ask(t("prompt_engine")).lower() or "g"
    base = ENGINES.get(engine, ENGINES["g"])
    print()
    print(ui.gray("   " + t("dorks_list")))
    for number, pattern in enumerate(DORK_PATTERNS, 1):
        print(ui.gray(f"   {number:02d} ") + ui.light(pattern.format(target)))
    pick = _ask(t("prompt_dork_pick"))
    if not pick.isdigit() or not 1 <= int(pick) <= len(DORK_PATTERNS):
        print(ui.gray("   " + t("dorks_bad_number")))
        return
    query = DORK_PATTERNS[int(pick) - 1].format(target)
    webbrowser.open(base + urllib.parse.quote(query))
    print(ui.gray("   " + t("dorks_opened")))
