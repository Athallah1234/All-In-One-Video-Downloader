import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from app.database import connect


@dataclass
class HistoryEntry:
    title: str
    url: str
    site: str = ""
    content_type: str = "video"
    format: str = ""
    quality: str = ""
    output_path: str = ""
    status: str = "completed"
    created_at: str = ""
    id: int | None = None
    downloaded_count: int = 0
    downloaded_size: int = 0


def _safe_non_negative(value):
    return value if isinstance(value,int) and not isinstance(value,bool) and value>=0 else 0


class HistoryService:
    def __init__(self, path: Path):
        self.path = Path(path)
        with connect(self.path):
            pass

    def add(self, entry: HistoryEntry) -> int:
        timestamp = entry.created_at or datetime.now().isoformat(timespec="seconds")
        with connect(self.path) as db:
            cursor = db.execute("INSERT INTO history(title,url,site,content_type,format,quality,output_path,status,created_at,downloaded_count,downloaded_size) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (entry.title, entry.url, entry.site, entry.content_type, entry.format, entry.quality, entry.output_path, entry.status, timestamp, _safe_non_negative(entry.downloaded_count), _safe_non_negative(entry.downloaded_size)))
            return int(cursor.lastrowid)

    def update_status(self, row_id: int, status: str, output_path: str | None = None):
        with connect(self.path) as db:
            if output_path is None:
                db.execute("UPDATE history SET status=? WHERE id=?", (status, row_id))
            else:
                db.execute("UPDATE history SET status=?, output_path=? WHERE id=?", (status, output_path, row_id))

    def complete(self,row_id,downloaded_count,downloaded_size):
        with connect(self.path) as db:db.execute("UPDATE history SET status='completed',downloaded_count=?,downloaded_size=? WHERE id=?",(_safe_non_negative(downloaded_count),_safe_non_negative(downloaded_size),row_id))

    def totals(self):
        with connect(self.path) as db:row=db.execute("SELECT COALESCE(SUM(downloaded_count),0),COALESCE(SUM(downloaded_size),0) FROM history WHERE status='completed'").fetchone()
        return _safe_non_negative(row[0]),_safe_non_negative(row[1])

    def list(self, search: str = "", status: str = "All") -> list[HistoryEntry]:
        sql, args = "SELECT * FROM history WHERE (title LIKE ? OR url LIKE ?)", [f"%{search}%", f"%{search}%"]
        if status and status != "All":
            sql += " AND status=?"; args.append(status)
        sql += " ORDER BY id DESC"
        with connect(self.path) as db:
            return [HistoryEntry(**dict(row)) for row in db.execute(sql, args)]

    def get(self, row_id: int) -> HistoryEntry | None:
        with connect(self.path) as db:
            row = db.execute("SELECT * FROM history WHERE id=?", (row_id,)).fetchone()
            return HistoryEntry(**dict(row)) if row else None

    def delete(self, row_id: int):
        with connect(self.path) as db: db.execute("DELETE FROM history WHERE id=?", (row_id,))

    def clear(self):
        with connect(self.path) as db: db.execute("DELETE FROM history")

    def export_csv(self, path: Path):
        rows = [asdict(x) for x in self.list()]
        with Path(path).open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(HistoryEntry.__dataclass_fields__))
            writer.writeheader(); writer.writerows(rows)

    def export_json(self, path: Path):
        Path(path).write_text(json.dumps([asdict(x) for x in self.list()], indent=2, ensure_ascii=False), encoding="utf-8")
