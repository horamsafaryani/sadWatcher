#!/usr/bin/env python3

import os
import sys
import sqlite3
import subprocess
import requests
import time
import logging
from datetime import datetime
from pathlib import Path
from dotenv import dotenv_values

# ─── Load .env ────────────────────────────────────────────────────────────────

def find_env_file() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    return base / ".env"


env_path = find_env_file()
if not env_path.exists():
    print(f"[FATAL] .env file not found at {env_path}")
    print("Please create a .env file. See .env.example for reference.")
    sys.exit(1)

cfg = dotenv_values(env_path)

# ─── Config ───────────────────────────────────────────────────────────────────

DB_PATH         = cfg.get("DB_PATH", "/var/lib/rebecca/db.sqlite3")
CHECK_INTERVAL  = int(cfg.get("CHECK_INTERVAL", "5"))
BOUNCE_PORTS    = [int(p.strip()) for p in cfg.get("BOUNCE_PORTS", "8080,8880").split(",")]
LOG_FILE        = cfg.get("LOG_FILE", "/var/lib/sadWatcher/sadWatcher.log")
LOG_LEVEL       = cfg.get("LOG_LEVEL", "INFO").upper()

# ─── Logging ──────────────────────────────────────────────────────────────────

Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
log = logging.getLogger("sadWatcher")

# ─── State ────────────────────────────────────────────────────────────────────

triggered_users: set[str] = set()

# ─── DB ───────────────────────────────────────────────────────────────────────

def read_users() -> list[tuple]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, data_limit, used_traffic
        FROM users
        WHERE data_limit > 0
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# ─── Method 6: ss -K ──────────────────────────────────────────────────────────

def kill_connections() -> bool:
    killed_any = False

    for port in BOUNCE_PORTS:
        try:
            r1 = subprocess.run(
                f"ss -K state established '( dport = :{port} )'",
                shell=True, capture_output=True, text=True
            )
            r2 = subprocess.run(
                f"ss -K state established '( sport = :{port} )'",
                shell=True, capture_output=True, text=True
            )

            if r1.returncode != 0 and r2.returncode != 0:
                log.error(f"ss -K failed on port {port}: {r1.stderr.strip()}")
                continue

            lines1 = [l for l in r1.stdout.strip().splitlines() if l and "State" not in l]
            lines2 = [l for l in r2.stdout.strip().splitlines() if l and "State" not in l]
            count = len(lines1) + len(lines2)

            if count > 0:
                log.info(f"Port {port}: killed {count} connection(s)")
                killed_any = True
            else:
                log.debug(f"Port {port}: no established connections found")

        except Exception as e:
            log.error(f"Port {port}: unexpected error: {e}")

    return killed_any

# ─── Cleanup ──────────────────────────────────────────────────────────────────

def cleanup_deleted_users(current_usernames: set):
    deleted = triggered_users - current_usernames
    for u in deleted:
        triggered_users.discard(u)
        log.info(f"Cleanup: '{u}' no longer in DB, removed from watchlist")

# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    log.info("=" * 50)
    log.info("sadWatcher started")
    log.info(f"DB path      : {DB_PATH}")
    log.info(f"Check every  : {CHECK_INTERVAL}s")
    log.info(f"Target ports : {BOUNCE_PORTS}")
    log.info(f"Log file     : {LOG_FILE}")
    log.info("=" * 50)

    while True:
        try:
            rows = read_users()
            current_usernames = {row[0] for row in rows}

            cleanup_deleted_users(current_usernames)

            over_limit = []
            for username, data_limit, used_traffic in rows:
                if used_traffic > data_limit and username not in triggered_users:
                    over_limit.append((username, data_limit, used_traffic))
                    triggered_users.add(username)

            if over_limit:
                for username, data_limit, used_traffic in over_limit:
                    log.warning(
                        f"OVER LIMIT: '{username}' "
                        f"used={used_traffic:,} / total={data_limit:,} bytes "
                        f"(+{used_traffic - data_limit:,})"
                    )
                log.warning(f"Killing connections on ports {BOUNCE_PORTS}...")
                kill_connections()

            for username, data_limit, used_traffic in rows:
                if username in triggered_users and used_traffic <= data_limit:
                    triggered_users.discard(username)
                    log.info(f"'{username}' traffic was reset, removed from watchlist")

        except sqlite3.OperationalError as e:
            log.error(f"DB error: {e}")
        except Exception as e:
            log.error(f"Unexpected error: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
