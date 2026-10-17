# VOID

Консольное меню в стиле RedTiger: белый ASCII-заголовок, анимированные
«капли» под ним, радужные github-ссылки и каркас функций под Roblox и OSINT.

```
██╗   ██╗ ██████╗ ██╗██████╗
██║   ██║██╔═══██╗██║██╔══██╗
██║   ██║██║   ██║██║██║  ██║
╚██╗ ██╔╝██║   ██║██║██║  ██║
 ╚████╔╝ ╚██████╔╝██║██████╔╝
  ╚═══╝   ╚═════╝ ╚═╝╚═════╝
```

## Запуск

```bash
python main.py
```

или двойным кликом по `run.bat`.

## Разделы и функции

| Раздел | Пункты |
| --- | --- |
| **Info** `[I]` | О проекте, Автор, Версия, Ссылки |
| **Osint** `[O]` | IP Lookup, Domain Info (RDAP), DNS Lookup, Username Tracker, URL Headers |
| **Roblox** `[R]` | User Lookup, User by ID, Avatar URL, Friends List, Groups List, Game Info, Game Servers, Join Game, API Status |
| **Utilities** `[U]` | System Info, Ping Roblox, Open Roblox Site, Password Generator, Hash Text, Base64 Enc/Dec, IP Generator, TODO Stub |

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
- `functions/roblox.py` — заготовки функций Roblox (публичные API, без авторизации)
- `functions/osint.py` — OSINT-заготовки (IP, домены, DNS, username, заголовки)
- `functions/utilities.py` — утилиты (система, пинг, генераторы, хеши)
- `run.bat` — запуск на Windows двойным кликом

## Как добавить свою функцию

1. Напиши функцию в `functions/roblox.py`, `functions/osint.py` или `functions/utilities.py`.
2. Добавь её в список `SECTIONS` в `main.py`: `("Название", твоя_функция)`.
3. Перезапусти меню — пункт появится в разделе.

---
by anubiz1337 · github.com/anubiz1337/void
