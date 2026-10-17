"""Local databases: downloaded once into data/, then reused offline.

Sources:
- sherlock-project/sherlock - site list for username search
- ipdeny.com - country IP ranges (aggregated zones)
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
IP_DIR = os.path.join(DATA_DIR, "ip_ranges")

SHERLOCK_URLS = [
    "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.json",
    "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock/resources/data.json",
    "https://raw.githubusercontent.com/sherlock-project/sherlock/master/data.json",
]
IPDENY_URL = "https://www.ipdeny.com/ipblocks/data/aggregated/{cc}-aggregated.zone"

TIMEOUT = 60
USER_AGENT = "VOID-Tools/1.0 (by anubiz1337)"


def _download(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read().decode("utf-8", "replace")


def _download_first(urls) -> str:
    last_error = None
    for url in urls:
        try:
            return _download(url)
        except Exception as error:  # noqa: BLE001
            last_error = error
    raise OSError(f"could not download: {last_error}")


def _read_local(path: str):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    return None


def _save(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)


# ---------- sherlock: site list ----------
def sherlock_sites(force: bool = False) -> dict:
    """Sherlock site database: name -> check rules (url, errorType, errorMsg...)."""
    path = os.path.join(DATA_DIR, "sherlock_data.json")
    text = None if force else _read_local(path)
    if text is None:
        text = _download_first(SHERLOCK_URLS)
        _save(path, text)
    return json.loads(text)


# ---------- ipdeny: country IP ranges ----------
def ip_ranges(country: str, force: bool = False):
    """List of CIDR ranges for a country (two letter code: ua, us, de...)."""
    country = country.strip().lower()
    if len(country) != 2 or not country.isalpha():
        raise ValueError("нужен код страны из двух букв (ua / us / de)")
    path = os.path.join(IP_DIR, f"{country}-aggregated.zone")
    text = None if force else _read_local(path)
    if text is None:
        text = _download(IPDENY_URL.format(cc=country))
        _save(path, text)
    return [line.strip() for line in text.splitlines() if line.strip()]


def ip_available():
    """Countries already downloaded locally."""
    if not os.path.isdir(IP_DIR):
        return []
    return sorted(
        name.split("-")[0]
        for name in os.listdir(IP_DIR)
        if name.endswith("-aggregated.zone")
    )
