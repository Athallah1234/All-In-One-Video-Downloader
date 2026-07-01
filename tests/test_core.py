from pathlib import Path
import sqlite3

from app.services.settings_service import SettingsService
from app.services.history_service import HistoryEntry, HistoryService


def test_settings_round_trip_and_reset(tmp_path):
    service = SettingsService(tmp_path / "settings.json")
    assert service.load()["theme"] == "System"
    service.save({"theme": "Dark", "concurrent_downloads": 3})
    assert service.load()["theme"] == "Dark"
    assert service.reset()["theme"] == "System"


def test_history_crud_and_exports(tmp_path):
    service = HistoryService(tmp_path / "history.db")
    row_id = service.add(HistoryEntry(title="Demo", url="https://example.com/v", site="generic", content_type="video", format="MP4", quality="1080p", output_path=str(tmp_path), status="completed"))
    assert service.list(search="Demo")[0].id == row_id
    service.update_status(row_id, "failed")
    assert service.list(status="failed")[0].status == "failed"
    service.export_csv(tmp_path / "history.csv")
    service.export_json(tmp_path / "history.json")
    assert (tmp_path / "history.csv").exists()
    assert (tmp_path / "history.json").exists()
    service.delete(row_id)
    assert service.list() == []


def test_history_migrates_legacy_database_idempotently(tmp_path):
    path=tmp_path/"legacy.db"
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE history (id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,url TEXT NOT NULL,site TEXT,content_type TEXT,format TEXT,quality TEXT,output_path TEXT,status TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        db.execute("INSERT INTO history(title,url,status) VALUES('Old','https://example.com','completed')")
    service=HistoryService(path); service=HistoryService(path); row=service.list()[0]
    assert row.downloaded_count==0 and row.downloaded_size==0
    with sqlite3.connect(path) as db:columns=[item[1] for item in db.execute("PRAGMA table_info(history)")]
    assert columns.count("downloaded_count")==1 and columns.count("downloaded_size")==1


def test_history_complete_and_totals_only_count_completed(tmp_path):
    service=HistoryService(tmp_path/"history.db")
    first=service.add(HistoryEntry("One","https://example.com/1",status="downloading"))
    service.add(HistoryEntry("Two","https://example.com/2",status="failed",downloaded_count=9,downloaded_size=999))
    service.complete(first,2,3072); row=service.get(first)
    assert row.status=="completed" and row.downloaded_count==2 and row.downloaded_size==3072
    assert service.totals()==(2,3072)
    service.delete(first); assert service.totals()==(0,0)
    service.clear(); assert service.totals()==(0,0)


def test_history_totals_normalize_invalid_values(tmp_path):
    service=HistoryService(tmp_path/"history.db"); row=service.add(HistoryEntry("One","https://example.com",status="downloading"))
    service.complete(row,True,-5)
    assert service.totals()==(0,0)
