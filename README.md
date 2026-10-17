```
██╗   ██╗ ██████╗ ██╗██████╗
██║   ██║██╔═══██╗██║██╔══██╗
██║   ██║██║   ██║██║██║  ██║
╚██╗ ██╔╝██║   ██║██║██║  ██║
 ╚████╔╝ ╚██████╔╝██║██████╔╝
  ╚═══╝   ╚═════╝ ╚═╝╚═════╝
```

# VOID-Tools (v0.6)

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

 [I] Info   [O] Osint   [R] Roblox   [U] Utilities          [N] Next

                    --------| Roblox |--------

  [01] User Lookup        [06] Game Info
  [02] User by ID         [07] Game Servers
  [03] Avatar URL         [08] Join Player
  [04] Friends List       [09] Join Game
  [05] Groups List        [10] API Status

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
  sections   : i = Info / o = Osint / r = Roblox / u = Utilities

Osint:
  [01] IP Lookup        : IP data via the ip-api.com API.
  [02] Domain Info      : WHOIS / RDAP domain data via rdap.org.
  [03] DNS Lookup       : A / AAAA records + reverse DNS (PTR).
  [04] Email MX         : MX records of an email / domain via Cloudflare DoH.
  [05] Username Tracker : track a username across 40+ sites (Sherlock database).
  [06] URL Headers      : response headers of a website.
  [07] Dork Builder     : search query builder (Google / Bing / DuckDuckGo).

Roblox:
  [01] User Lookup      : username -> public profile data.
  [02] User by ID       : profile by user id.
  [03] Avatar URL       : avatar headshot URL.
  [04] Friends List     : public friends list.
  [05] Groups List      : groups and roles.
  [06] Game Info        : game data by place id.
  [07] Game Servers     : public servers of a game.
  [08] Join Player      : enter a username to find the game a player is in and
                          join it, or enter a place id to search the game's
                          public servers and join a specific one.
  [09] Join Game        : launch Roblox into a place.
  [10] API Status       : check Roblox API availability.

Utilities:
  [01] System Info        : OS / Python information.
  [02] Ping Host          : latency check for a host (default roblox.com).
  [03] Open Roblox Site   : open roblox.com in the browser.
  [04] Password Generator : crypto-strong password (secrets module).
  [05] Hash Text          : md5 / sha1 / sha256 / sha512.
  [06] Base64 Enc/Dec     : base64 encode / decode.
  [07] IP Generator       : IPs from real country ranges (ipdeny database).
  [08] Update Databases   : refresh the local databases.
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
- `functions/utilities.py` - utilities
- `functions/database.py` - local database manager

## 👨‍💻 Credits:

- Developed by: **anubiz1337**
- GitHub: [github.com/anubiz1337](https://github.com/anubiz1337)
- License: **MIT License**
- Version: **v0.6**
