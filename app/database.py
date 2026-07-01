import sqlite3
from pathlib import Path


def connect(path: Path) -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("""CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, url TEXT NOT NULL,
        site TEXT, content_type TEXT, format TEXT, quality TEXT, output_path TEXT,
        status TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    columns={row[1] for row in connection.execute("PRAGMA table_info(history)")}
    if "downloaded_count" not in columns:connection.execute("ALTER TABLE history ADD COLUMN downloaded_count INTEGER NOT NULL DEFAULT 0")
    if "downloaded_size" not in columns:connection.execute("ALTER TABLE history ADD COLUMN downloaded_size INTEGER NOT NULL DEFAULT 0")
    connection.commit()
    return connection
