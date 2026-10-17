```
██╗   ██╗ ██████╗ ██╗██████╗
██║   ██║██╔═══██╗██║██╔══██╗
██║   ██║██║   ██║██║██║  ██║
╚██╗ ██╔╝██║   ██║██║██║  ██║
 ╚████╔╝ ╚██████╔╝██║██████╔╝
  ╚═══╝   ╚═════╝ ╚═╝╚═════╝
```

# VOID-Tools (v1.0)

VOID is a terminal multi-tool dedicated to OSINT and Roblox. White ASCII menu,
rainbow github links, local databases and an English / Russian interface.
No external dependencies - Python standard library only.

## ⚠️ Disclaimer:

This tool is intended exclusively for educational and lawful use. Any malicious
use is strictly prohibited. You are responsible for how you use it and for
following the terms of service of the sites it queries.

## 📝 Description:

- 🖥️ Compatible with Windows and Linux (Linux runs in a static, non-animated mode).
- 🌐 Interface language: English / Russian, switchable inside the tool (default: English).
- 🤍 Minimal white theme, the only colored elements are the github links.
- 🗄️ Local databases: 480+ sites (Sherlock) and real country IP ranges (ipdeny).
- 📦 No external dependencies - Python standard library only.
- 🧩 Easy to extend: write a function, hook it into `SECTIONS`.

## 📸 Preview:

```
                github.com/anubiz1337

    [I] Info  [O] Osint  [W] Web  [R] Roblox  [F] Fun  [U] Utils    [N] Next

   ────────┤ Roblox ├────────

   [01] User Lookup              [09] Group Info
   [02] User by ID               [10] Group Members
   [03] Avatar URL               [11] User Games
   [04] Friends List             [12] Game Search
   [05] Groups List              [13] Join Player
   [06] Game Info                [14] Join Game
   [07] Game Servers             [15] API Status
   [08] Game Passes

  Command:
  by anubiz1337  ·  github.com/anubiz1337/void
```

## ⚙️ Installation:

1. Install the latest version of Python:

- Windows:

```
Download Here (The "PATH" option must be enabled during installation)
```

- Linux:

```
sudo apt install python3 -y
```

2. Install the latest version of Git:

- Windows:

```
Download Here (The "PATH" option must be enabled during installation)
```

- Linux:

```
sudo apt install git -y
```

3. Clone the repository:

```
git clone https://github.com/anubiz1337/void.git
```

4. Enter the project folder:

```
cd void
```

5. Launch the tool:

- Windows:

```
python main.py
```

- Linux:

```
python3 main.py
```

On Windows you can also just double-click `run.bat`.

## 🔄 Update:

1. Enter the project folder:

```
cd void
```

2. Update launch:

```
git pull
```

## 🌐 Interface language:

- Default language is **English**.
- Switch to Russian inside the tool: `Info -> Language`, or type `lang` in the command line.

## 🚀 Features:

```
Menu:
  lang / l   : switch interface language (EN / RU)
  n / next   : next section
  q / quit   : exit
  sections   : i = Info / o = Osint / w = Web / r = Roblox / f = Fun / u = Utils

Osint:
  [01] IP Lookup        : IP data + proxy / hosting / mobile flags (ip-api.com).
  [02] Domain Info      : WHOIS / RDAP domain data via rdap.org.
  [03] DNS Lookup       : A / AAAA records + reverse DNS (PTR).
  [04] Subdomains       : subdomain list from certificate transparency (crt.sh).
  [05] Email MX         : MX records of an email / domain via Cloudflare DoH.
  [06] Username Tracker : track a username across 40+ sites (Sherlock database).
  [07] GitHub Lookup    : public GitHub profile data by username.
  [08] IP Ports         : open ports / hostnames / vulns of an IP (Shodan InternetDB).
  [09] Reverse IP       : domains hosted on the same IP (HackerTarget).
  [10] SSL Certificate  : TLS certificate info (issuer, dates, SANs).
  [11] Wayback Machine  : first and latest snapshots of a site (archive.org).
  [12] Email Security   : SPF and DMARC records (Cloudflare DoH).
  [13] IP Whois         : network registration data of an IP (RDAP).

Web:
  [01] URL Headers      : response headers of a website.
  [02] Dork Builder     : search query builder (Google / Bing / DuckDuckGo).
  [03] Expand URL       : print the redirect chain and the final address.
  [04] Port Scan        : quick check of the most common ports.
  [05] Ping Host        : latency check for a host (default roblox.com).
  [06] Open Roblox Site : open roblox.com in the browser.
  [07] Robots.txt       : rules from the robots.txt of a site.
  [08] Site Info        : title / description / Open Graph meta tags.
  [09] Security Headers : HSTS / CSP / X-Frame-Options check with a score.

Roblox:
  [01] User Lookup      : username -> public profile data.
  [02] User by ID       : profile by user id.
  [03] Avatar URL       : avatar headshot URL.
  [04] Friends List     : public friends list.
  [05] Groups List      : groups and roles.
  [06] Game Info        : game data by place id (+ icon url, votes, rating).
  [07] Game Servers     : public servers of a game.
  [08] Game Passes      : game passes of a game with prices.
  [09] Group Info       : group data by id or name search.
  [10] Group Members    : public member list of a group (role + user id).
  [11] User Games       : games a user created (visits + place id).
  [12] Game Search      : find games by name, show info and join.
  [13] Join Player      : enter a username to find the game a player is in and
                          join it, or enter a place id to search the game's
                          public servers and join a specific one.
  [14] Join Game        : launch Roblox into a place.
  [15] API Status       : check Roblox API availability.

Fun:
  [01] Vaporwave Text : convert text to ｖａｐｏｒｗａｖｅ full-width style.
  [02] Leet Speak     : convert text to l33t speak.
  [03] Upside Down    : ʇxǝʇ uʍop ǝpᴉsdn.
  [04] Hacker ID      : random "hacker" nickname generator.
  [05] Coin Flip      : flip a coin with a spin animation.
  [06] Random Game    : pick a random Roblox game and optionally join it.

Utilities:
  [01] System Info        : OS / Python information.
  [02] Password Generator : crypto-strong password (secrets module).
  [03] Hash Text          : md5 / sha1 / sha256 / sha512.
  [04] Base64 Enc/Dec     : base64 encode / decode.
  [05] IP Generator       : IPs from real country ranges (ipdeny database).
  [06] Update Databases   : refresh the local databases.
```

## 🗄️ Databases:

| Database | Source | Used by |
| --- | --- | --- |
| `sherlock_data.json` | github.com/sherlock-project/sherlock | Username Tracker |
| `ip_ranges/*.zone` | ipdeny.com | IP Generator |

They are downloaded automatically on first use into `data/` (not tracked by git).

## 🧩 Structure:

- `main.py` - menu, animation, key handling
- `ui.py` - ANSI colors, ASCII art, frame rendering
- `i18n.py` - English / Russian interface strings
- `functions/roblox.py` - Roblox API functions
- `functions/osint.py` - OSINT functions
- `functions/web.py` - web functions
- `functions/fun.py` - fun functions (text styles, coin, random game)
- `functions/utilities.py` - utilities
- `functions/database.py` - local database manager

## 👨‍💻 Credits:

- Developed by: **anubiz1337**
- GitHub: [github.com/anubiz1337](https://github.com/anubiz1337)
- License: **MIT License**
- Version: **v1.0**
