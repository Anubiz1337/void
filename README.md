# VOID

Консольное меню в стиле RedTiger: белый ASCII-заголовок, анимированные
«капли» под ним, радужные github-ссылки, каркас функций под Roblox и OSINT,
реальные базы данных из интернета.

```
██╗   ██╗ ██████╗ ██╗██████╗
██║   ██║██╔═══██╗██║██╔══██╗
██║   ██║██║   ██║██║██║  ██║
╚██╗ ██╔╝██║   ██║██║██║  ██║
 ╚████╔╝ ╚██████╔╝██║██████╔╝
  ╚═══╝   ╚═════╝ ╚═╝╚═════╝
```

## ⚡ Что нового в v0.3

- Модуль `random` полностью убран — вместо него криптостойкий `secrets`
- Подключены **реальные базы данных** (качаются один раз в `data/`, дальше офлайн):
  - **Sherlock DB** (~480 сайтов) — Username Tracker ищет ник на ~40 сайтах из базы + GitHub / Reddit / Twitch / Roblox
  - **ipdeny.com** — IP Generator выдаёт IP из настоящих диапазонов стран (например, Украина: ~2600 диапазонов, 9 млн адресов)
- Новый пункт меню: **Utilities → Update Databases** — принудительно обновить базы

## Запуск

```bash
python main.py
```

или двойным кликом по `run.bat`.

## Разделы и функции

| Раздел | Пункты |
| --- | --- |
| **Info** `[I]` | О проекте, Автор, Версия, Ссылки |
| **Osint** `[O]` | IP Lookup, Domain Info (RDAP), DNS Lookup, Username Tracker (по базе Sherlock), URL Headers |
| **Roblox** `[R]` | User Lookup, User by ID, Avatar URL, Friends List, Groups List, Game Info, Game Servers, Join Game, API Status |
| **Utilities** `[U]` | System Info, Ping Roblox, Open Roblox Site, Password Generator, Hash Text, Base64 Enc/Dec, IP Generator (по базе ipdeny), Update Databases, TODO Stub |

## Базы данных (data/)

| База | Источник | Для чего |
| --- | --- | --- |
| `sherlock_data.json` | github.com/sherlock-project/sherlock | база сайтов для поиска username |
| `ip_ranges/*.zone` | ipdeny.com | реальные IP-диапазоны стран |

Качаются автоматически при первом использовании, лежат локально, в git не попадают.

## Управление

| Клавиши | Действие |
| --- | --- |
| `01`–`09` | запустить пункт меню |
| `I` / `O` / `R` / `U` | перейти к разделу |
| `N` или стрелки `←` `→` | следующий раздел |
| `Q` | выход |

## Структура

- `main.py` — меню, анимация, обработка клавиш
- `ui.py` — ANSI-цвета, ASCII-арт, отрисовка кадра
- `functions/roblox.py` — функции Roblox (публичные API, без авторизации)
- `functions/osint.py` — OSINT (IP, домены, DNS, username, заголовки)
- `functions/utilities.py` — утилиты (система, генераторы, хеши, базы)
- `functions/database.py` — менеджер локальных баз данных
- `run.bat` — запуск на Windows двойным кликом

## Как добавить свою функцию

1. Напиши функцию в `functions/roblox.py`, `functions/osint.py` или `functions/utilities.py`.
2. Добавь её в список `SECTIONS` в `main.py`: `("Название", твоя_функция)`.
3. Перезапусти меню — пункт появится в разделе.

---
by anubiz1337 · github.com/anubiz1337/void
