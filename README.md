# sadWatcher

**sadWatcher** is a lightweight daemon that monitors [Rebecca](https://github.com/rebeccapanel/Rebecca) / [Marzban](https://github.com/Gozargah/Marzban) / [PasarGuard](https://github.com/PasarGuard/panel) user traffic in real time and immediately kills active xray connections when a user exceeds their data limit — using `ss -K` to send TCP RST packets directly to established connections.

---

## Why sadWatcher?

Rebecca/Marzban marks over-limit users as disabled in the database, but active connections persist until xray reloads. sadWatcher closes those connections within seconds without restarting the entire panel.

Supports:
- Rebecca
- Marzban
- PasarGuard

Default database paths:
- Rebecca: `/var/lib/rebecca/db.sqlite3`
- Marzban: `/var/lib/marzban/db.sqlite3`
- PasarGuard: `/var/lib/pasarguard/db.sqlite3`

---

## How it works

1. Reads the SQLite database every N seconds
2. Detects users whose `used_traffic > data_limit`
3. Sends TCP RST to all established connections on the configured xray ports via `ss -K`
4. Logs everything to file and stdout

---

## Installation

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/horamsafaryani/sadWatcher/latest/install.sh)"
```

The installer will ask you:
- Path to the Rebecca/Marzban SQLite database
- Which xray ports to watch
- Check interval (seconds)
- Log level

---

## Configuration

Config lives in `/var/lib/sadWatcher/.env`:

| Variable | Default | Description |
|---|---|---|
| `DB_PATH` | `/var/lib/rebecca/db.sqlite3` | Path to SQLite DB (Rebecca / Marzban / PasarGuard) |
| `CHECK_INTERVAL` | `5` | Seconds between checks |
| `BOUNCE_PORTS` | `8080,8880` | xray ports (comma separated) |
| `LOG_FILE` | `/var/lib/sadWatcher/sadWatcher.log` | Log file path |
| `LOG_LEVEL` | `INFO` | DEBUG / INFO / WARNING / ERROR |

After editing `.env`, restart the service:
```bash
systemctl restart sadWatcher
```

---

## Useful commands

```bash
systemctl status sadWatcher          # check status
journalctl -fu sadWatcher            # live logs
tail -f /var/lib/sadWatcher/sadWatcher.log   # log file
```

---

## Uninstall

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/horamsafaryani/sadWatcher/latest/install.sh)" -- uninstall
```

---

## Requirements

- Linux with `ss` (iproute2) — any modern distro
- Root access (needed for `ss -K`)
- Rebecca, Marzban or PasarGuard panel with SQLite database

---

## License

MIT
