"""
Week 8 demo: SQLite BACKUP (not replication).

    python scripts/backup_db.py

Uses SQLite's official backup API, which produces a consistent copy even if
the app is running. A backup is a snapshot at one moment in time. Replication
(see docs/WEEK8.md) keeps another database continuously up to date.
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE = BASE_DIR / "db.sqlite3"
BACKUP_DIR = BASE_DIR / "backups"


def main():
    if not SOURCE.exists():
        sys.exit(f"Database not found: {SOURCE}. Run 'python manage.py migrate' first.")
    BACKUP_DIR.mkdir(exist_ok=True)
    target = BACKUP_DIR / f"db-{datetime.now():%Y%m%d-%H%M%S}.sqlite3"
    src = sqlite3.connect(SOURCE)
    dst = sqlite3.connect(target)
    with dst:
        src.backup(dst)
    src.close()
    dst.close()
    print(f"Backup created: {target}")


if __name__ == "__main__":
    main()
