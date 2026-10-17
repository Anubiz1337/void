"""Web functions: headers, dorks, redirects, ports."""
import concurrent.futures
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

import ui
from i18n import t

TIMEOUT = 15
USER_AGENT = "VOID-Tools/0.8 (by anubiz1337)"

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
