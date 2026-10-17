"""Web functions: headers, dorks, redirects, ports."""
import concurrent.futures
import re
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

import ui
from i18n import t

TIMEOUT = 15
USER_AGENT = "VOID-Tools/1.0 (by anubiz1337)"

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

COMMON_PORTS = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    143: "imap",
    443: "https",
    445: "smb",
    3306: "mysql",
    3389: "rdp",
    5432: "postgres",
    5900: "vnc",
    8080: "http-alt",
    8443: "https-alt",
    25565: "minecraft",
}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _ask(prompt):
    return input(ui.light("   " + prompt)).strip()


def _fetch(url, limit=None, timeout=TIMEOUT):
    """GET a page as text (optionally only the first `limit` bytes)."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read(limit) if limit else response.read()
        return response.status, body.decode("utf-8", "replace")


def _pairs(pairs):
    for label, value in pairs:
        if value not in (None, ""):
            print(ui.gray(f"   {label:<14} ") + ui.light(str(value)))


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


def expand_url():
    """Print the redirect chain of a URL and the final address."""
    url = _ask(t("prompt_url"))
    if not url:
        print(ui.gray("   " + t("cancelled")))
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        for _ in range(10):
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with opener.open(request, timeout=TIMEOUT) as response:
                    print(ui.gray("   " + t("headers_status").format(response.status)))
                    print(ui.gray("   " + t("expand_final")) + ui.light(url))
                    return
            except urllib.error.HTTPError as error:
                if error.code not in (301, 302, 303, 307, 308):
                    print(ui.red("   " + t("headers_http").format(error.code)))
                    return
                location = error.headers.get("Location")
                if not location:
                    print(ui.red("   " + t("headers_http").format(error.code)))
                    return
                url = urllib.parse.urljoin(url, location)
                print(ui.gray("   → ") + ui.light(url))
    except urllib.error.URLError as error:
        print(ui.red("   " + t("expand_failed").format(error.reason)))
        return
    print(ui.gray("   " + t("expand_final")) + ui.light(url))


def _check_port(host, port, timeout=0.6):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def port_scan():
    """Quick scan of the most common ports (threaded)."""
    host = _ask(t("prompt_scan_host"))
    if not host:
        print(ui.gray("   " + t("cancelled")))
        return
    try:
        socket.gethostbyname(host)
    except socket.gaierror as error:
        print(ui.red("   " + t("portscan_failed").format(error)))
        return
    start = time.perf_counter()
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = {
            executor.submit(_check_port, host, port): port for port in COMMON_PORTS
        }
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                open_ports.append(futures[future])
    open_ports.sort()
    if not open_ports:
        print(ui.gray("   " + t("portscan_none")))
        return
    print(ui.gray("   " + t("portscan_done").format(len(open_ports))))
    for port in open_ports:
        print(ui.white(f"   {port:<6} ") + ui.gray(COMMON_PORTS.get(port, "?")))
    print(ui.gray(f"   {time.perf_counter() - start:.1f}s"))


def ping_host():
    host = _ask(t("prompt_ping_host")) or "roblox.com"
    if not host.startswith(("http://", "https://")):
        host = "https://" + host
    start = time.perf_counter()
    try:
        request = urllib.request.Request(host, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            response.read(1)
        ms = (time.perf_counter() - start) * 1000
        print(ui.light("   " + t("ping_pong").format(ms)))
    except Exception as error:
        print(ui.red("   " + t("ping_fail").format(error)))


def open_roblox_site():
    webbrowser.open("https://www.roblox.com")
    print(ui.gray("   " + t("open_opened")))


def robots_txt():
    """Rules from the robots.txt of a site."""
    url = _ask(t("prompt_url"))
    if not url:
        print(ui.gray("   " + t("cancelled")))
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parts = urllib.parse.urlsplit(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    try:
        _status, body = _fetch(robots_url, limit=200000)
    except urllib.error.HTTPError:
        print(ui.gray("   " + t("robots_none")))
        return
    except urllib.error.URLError as error:
        print(ui.red("   " + t("headers_unreachable").format(error.reason)))
        return
    rules = [
        line.strip()
        for line in body.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not rules:
        print(ui.gray("   " + t("robots_none")))
        return
    print(ui.gray("   " + t("robots_rules").format(len(rules))))
    for line in rules[:15]:
        print(ui.light(f"   · {line[:70]}"))
    if len(rules) > 15:
        print(ui.gray("   " + t("robots_more")))


def _meta(body, key, attr="name"):
    """Find a <meta> tag by name / property and return its content."""
    for tag in re.findall(r"<meta\b[^>]*>", body, re.I):
        if re.search(rf'{attr}\s*=\s*["\']{re.escape(key)}["\']', tag, re.I):
            content = re.search(r'content\s*=\s*["\']([^"\']*)["\']', tag, re.I)
            if content:
                return content.group(1).strip()
    return None


def site_info():
    """Title, description and Open Graph meta tags of a page."""
    url = _ask(t("prompt_url"))
    if not url:
        print(ui.gray("   " + t("cancelled")))
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        _status, body = _fetch(url, limit=300000)
    except urllib.error.HTTPError as error:
        print(ui.red("   " + t("headers_http").format(error.code)))
        return
    except urllib.error.URLError as error:
        print(ui.red("   " + t("headers_unreachable").format(error.reason)))
        return
    title = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    rows = [
        (t("label_title"), title.group(1).strip() if title else None),
        (t("label_desc"), _meta(body, "description")),
        (t("label_generator"), _meta(body, "generator")),
        (t("label_og_title"), _meta(body, "og:title", "property")),
        (t("label_og_image"), _meta(body, "og:image", "property")),
    ]
    if not any(value for _label, value in rows):
        print(ui.gray("   " + t("siteinfo_empty")))
        return
    print()
    _pairs([(label, value[:110] if isinstance(value, str) else value) for label, value in rows])


def security_headers():
    """Check the main HTTP security headers of a site."""
    url = _ask(t("prompt_url"))
    if not url:
        print(ui.gray("   " + t("cancelled")))
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            headers = {key.lower(): value for key, value in response.headers.items()}
    except urllib.error.HTTPError as error:
        headers = {key.lower(): value for key, value in error.headers.items()}
    except urllib.error.URLError as error:
        print(ui.red("   " + t("headers_unreachable").format(error.reason)))
        return
    checks = [
        (t("label_hsts"), "strict-transport-security"),
        (t("label_csp"), "content-security-policy"),
        (t("label_frame"), "x-frame-options"),
        (t("label_nosniff"), "x-content-type-options"),
        (t("label_referrer"), "referrer-policy"),
    ]
    present = 0
    print()
    for label, header in checks:
        if header in headers:
            present += 1
            print(ui.gray(f"   {label:<24}") + ui.light(t("yes")))
        else:
            print(ui.gray(f"   {label:<24}") + ui.red(t("no")))
    print(ui.gray("   " + t("sechdr_score").format(present, len(checks))))
