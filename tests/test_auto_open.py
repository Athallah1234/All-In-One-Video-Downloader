from types import SimpleNamespace
from pathlib import Path

import pytest

from app.services.ytdlp_service import DownloadRequest
from app.ui.main_window import MainWindow,safe_output_files,completed_file_stats


@pytest.fixture
def window(qtbot,monkeypatch,tmp_path):
    monkeypatch.setattr("app.ui.main_window.SETTINGS_PATH",tmp_path/"settings.json"); monkeypatch.setattr("app.ui.main_window.HISTORY_PATH",tmp_path/"history.db")
    value=MainWindow(); qtbot.addWidget(value); return value


def worker_stub(output_dir,open_after_download=True,playlist_selection_mode="all"):
    request=DownloadRequest("https://example.com/v",output_dir,open_after_download=open_after_download,playlist_selection_mode=playlist_selection_mode)
    return SimpleNamespace(request=request)


def test_safe_output_files_keeps_existing_contained_files(tmp_path):
    first=tmp_path/"a.mp4"; first.write_bytes(b"a"); nested=tmp_path/"sub"/"b.mp3"; nested.parent.mkdir(); nested.write_bytes(b"b")
    assert safe_output_files(tmp_path,[str(first),str(nested),str(first)])==(first.resolve(),nested.resolve())


def test_safe_output_files_rejects_missing_directory_and_outside_paths(tmp_path):
    outside=tmp_path.parent/"outside.mp4"; outside.write_bytes(b"x"); directory=tmp_path/"folder"; directory.mkdir(); missing=tmp_path/"missing.mp4"
    assert safe_output_files(tmp_path,[str(outside),str(directory),str(missing),None])==()
    outside.unlink()


def test_safe_output_files_resolves_relative_paths_inside_output(tmp_path):
    result=tmp_path/"relative.mp4"; result.write_bytes(b"x")
    assert safe_output_files(tmp_path,["relative.mp4"] )==(result.resolve(),)


def test_completed_file_stats_counts_unique_file_sizes(tmp_path):
    first=tmp_path/"a"; second=tmp_path/"b"; first.write_bytes(b"123"); second.write_bytes(b"12345")
    assert completed_file_stats((first,second,first))==(2,8,0)


def test_completed_file_stats_contains_stat_failures(tmp_path,monkeypatch):
    path=tmp_path/"a"; path.write_bytes(b"x"); original=Path.stat
    def selective_stat(self):
        if self==path:raise OSError("gone")
        return original(self)
    monkeypatch.setattr(Path,"stat",selective_stat)
    assert completed_file_stats((path,))==(0,0,1)


def test_auto_open_single_file_after_success(window,tmp_path):
    result=tmp_path/"video.mp4"; result.write_bytes(b"x"); opened=[]
    window._open_completed_result(worker_stub(tmp_path),{"type":"video","output_paths":(str(result),)},lambda url:opened.append(url.toLocalFile()) or True)
    assert [Path(value).resolve() for value in opened]==[result.resolve()]


def test_auto_open_playlist_opens_folder_once(window,tmp_path):
    first=tmp_path/"a.mp4"; second=tmp_path/"b.mp4"; first.write_bytes(b"a"); second.write_bytes(b"b"); opened=[]
    window._open_completed_result(worker_stub(tmp_path,playlist_selection_mode="selected"),{"type":"playlist","output_paths":(str(first),str(second))},lambda url:opened.append(url.toLocalFile()) or True)
    assert [Path(value).resolve() for value in opened]==[tmp_path.resolve()]


def test_auto_open_skips_opt_out_shutdown_and_missing_paths(window,tmp_path):
    calls=[]; opener=lambda url:calls.append(url) or True
    window._open_completed_result(worker_stub(tmp_path,False),{"output_paths":()},opener)
    window._close_when_idle=True; window._open_completed_result(worker_stub(tmp_path),{"output_paths":()},opener); window._close_when_idle=False
    window._open_completed_result(worker_stub(tmp_path),{"output_paths":(str(tmp_path/"missing.mp4"),)},opener)
    assert calls==[]
    assert "tidak ditemukan" in window.logs.view.toPlainText().lower()


@pytest.mark.parametrize("opener",[lambda url:False,lambda url:(_ for _ in ()).throw(RuntimeError("gagal"))])
def test_auto_open_contains_launcher_failures(window,tmp_path,opener):
    result=tmp_path/"video.mp4"; result.write_bytes(b"x")
    window._open_completed_result(worker_stub(tmp_path),{"output_paths":(str(result),)},opener)
    assert "tidak dapat membuka" in window.logs.view.toPlainText().lower()


def test_download_done_persists_file_totals_and_refreshes_status(window,tmp_path):
    first=tmp_path/"a.mp4"; second=tmp_path/"b.mp4"; first.write_bytes(b"123"); second.write_bytes(b"12345")
    worker=worker_stub(tmp_path,False); worker.history_id=window.history_service.add(__import__("app.services.history_service",fromlist=["HistoryEntry"]).HistoryEntry("Job","https://example.com",status="downloading"))
    window.download_done(worker,{"title":"Done","output_paths":(str(first),str(second))})
    row=window.history_service.get(worker.history_id)
    assert (row.downloaded_count,row.downloaded_size)==(2,8)
    assert window.download_count_label.text()=="Download selesai: 2 file"
    assert window.download_size_label.text()=="Total ukuran: 8 B"
