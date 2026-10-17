"""OSINT functions: IP, domains, DNS, subdomains, email MX, username search."""
import concurrent.futures
import json
import secrets
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

import ui
from i18n import t

from . import database

TIMEOUT = 15
USER_AGENT = "VOID-Tools/0.9 (by anubiz1337)"


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


def _dns_json(name, record_type):
    """Cloudflare DNS-over-HTTPS query (JSON)."""
    url = f"https://cloudflare-dns.com/dns-query?name={urllib.parse.quote(name)}&type={record_type}"
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/dns-json"}
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8", "replace"))


def _mx_records(domain):
    """MX records via Cloudflare DNS-over-HTTPS (JSON)."""
    data = _dns_json(domain, "MX")
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


def ip_ports():
    """Open ports, hostnames and known issues of an IP (Shodan InternetDB)."""
    ip = _ask(t("prompt_ip_only"))
    if not ip:
        print(ui.gray("   " + t("cancelled")))
        return
    status, data = _request(f"https://internetdb.shodan.io/{ip}")
    if status == 404:
        print(ui.gray("   " + t("ports_none")))
        return
    if status != 200 or not isinstance(data, dict):
        print(ui.red("   " + t("fetch_failed")))
        return
    print()
    _pairs([
        (t("label_ip"), data.get("ip")),
        (t("label_ports"), ", ".join(str(port) for port in data.get("ports") or []) or "-"),
        (t("label_hostnames"), ", ".join((data.get("hostnames") or [])[:5])[:80] or "-"),
        (t("label_tags"), ", ".join((data.get("tags") or [])[:5]) or "-"),
        (t("label_vulns"), ", ".join((data.get("vulns") or [])[:8]) or "-"),
    ])


def reverse_ip():
    """Domains hosted on the same IP (HackerTarget reverse IP lookup)."""
    target = _ask(t("prompt_scan_host"))
    if not target:
        print(ui.gray("   " + t("cancelled")))
        return
    url = f"https://api.hackertarget.com/reverseiplookup/?q={urllib.parse.quote(target)}"
    status, data = _request(url, timeout=30)
    if status != 200 or not isinstance(data, str):
        print(ui.red("   " + t("fetch_failed")))
        return
    text = data.strip()
    low = text.lower()
    if low.startswith("error") or "quota" in low or "api count" in low:
        print(ui.red("   " + t("revip_limit")))
        return
    domains = [line.strip() for line in text.splitlines() if line.strip()]
    if not domains:
        print(ui.gray("   " + t("revip_none")))
        return
    print(ui.gray("   " + t("revip_found").format(len(domains))))
    for name in domains[:20]:
        print(ui.light(f"   · {name}"))
    if len(domains) > 20:
        print(ui.gray("   " + t("revip_truncated")))


def ssl_info():
    """TLS certificate of a host (standard library only)."""
    host = _clean_domain(_ask(t("prompt_host")))
    if not host:
        print(ui.gray("   " + t("cancelled")))
        return
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=TIMEOUT) as raw:
            with context.wrap_socket(raw, server_hostname=host) as tls:
                cert = tls.getpeercert()
    except Exception as error:
        print(ui.red("   " + t("ssl_failed").format(error)))
        return
    subject = dict(pair[0] for pair in cert.get("subject", []))
    issuer = dict(pair[0] for pair in cert.get("issuer", []))
    days_left = "-"
    try:
        days_left = int((ssl.cert_time_to_seconds(cert.get("notAfter", "")) - time.time()) / 86400)
    except Exception:
        pass
    sans = [value for kind, value in cert.get("subjectAltName", []) if kind == "DNS"]
    print()
    _pairs([
        (t("label_cn"), subject.get("commonName", "-")),
        (t("label_issuer"), issuer.get("organizationName") or issuer.get("commonName", "-")),
        (t("label_valid_from"), cert.get("notBefore", "-")),
        (t("label_valid_to"), cert.get("notAfter", "-")),
        (t("label_days_left"), days_left),
        (t("label_sans"), ", ".join(sans[:6])[:80] or "-"),
    ])


def wayback():
    """First and latest snapshot of a site (Internet Archive)."""
    domain = _clean_domain(_ask(t("prompt_domain")))
    if not domain:
        print(ui.gray("   " + t("cancelled")))
        return

    def stamp(value):
        value = str(value or "")
        return f"{value[0:4]}-{value[4:6]}-{value[6:8]}" if len(value) >= 8 else "-"

    status, data = _request(f"https://archive.org/wayback/available?url={domain}", timeout=30)
    snapshot = None
    if status == 200 and isinstance(data, dict):
        snapshot = (data.get("archived_snapshots") or {}).get("closest")
    if not snapshot:
        print(ui.gray("   " + t("wayback_none")))
        return
    first = "-"
    status, data = _request(
        f"https://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=1&fl=timestamp",
        timeout=30,
    )
    if status == 200 and isinstance(data, list) and len(data) > 1:
        first = stamp(data[1][0])
    print()
    _pairs([
        (t("label_domain"), domain),
        (t("wayback_first"), first),
        (t("wayback_latest"), stamp(snapshot.get("timestamp"))),
        (t("label_status"), snapshot.get("status")),
    ])
    print(ui.gray("   " + t("wayback_url")) + ui.light(snapshot.get("url", "")))


def email_security():
    """SPF and DMARC records of a domain."""
    raw = _ask(t("prompt_email"))
    if not raw:
        print(ui.gray("   " + t("cancelled")))
        return
    domain = raw.split("@")[-1].strip().lower()
    try:
        spf_answer = _dns_json(domain, "TXT")
        dmarc_answer = _dns_json(f"_dmarc.{domain}", "TXT")
    except Exception:
        print(ui.red("   " + t("emailsec_failed")))
        return

    def find_record(answer, prefix):
        for entry in answer.get("Answer", []):
            value = str(entry.get("data", "")).strip('"')
            if value.lower().startswith(prefix):
                return value
        return None

    spf = find_record(spf_answer, "v=spf1")
    dmarc = find_record(dmarc_answer, "v=dmarc1")
    print()
    if spf:
        print(ui.gray(f"   {t('label_spf'):<7} ") + ui.light(spf[:110]))
    else:
        print(ui.red("   " + t("emailsec_none_spf")))
    if dmarc:
        print(ui.gray(f"   {t('label_dmarc'):<7} ") + ui.light(dmarc[:110]))
    else:
        print(ui.red("   " + t("emailsec_none_dmarc")))

