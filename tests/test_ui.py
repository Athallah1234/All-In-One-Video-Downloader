import pytest

from app.services.history_service import HistoryService,HistoryEntry
from app.ui.downloader_tab import DownloaderTab
from app.ui.history_tab import HistoryTab
from app.ui.logs_tab import LogsTab
from app.ui.main_window import MainWindow
from PySide6.QtWidgets import QFormLayout,QMessageBox
from PySide6.QtCore import QMetaMethod,Qt


def combo_items(combo):
    return [combo.itemText(index) for index in range(combo.count())]


def analyzed_items():
    return ({"index":1,"title":"Satu"},{"index":2,"title":"Dua"},{"index":3,"title":"Tiga"})


@pytest.mark.parametrize("value,expected", [(0,"0"),(1234567,"1.234.567"),(None,"Tidak tersedia"),(True,"Tidak tersedia"),(-1,"Tidak tersedia"),("10","Tidak tersedia")])
def test_format_count_is_total(value, expected):
    assert DownloaderTab.format_count(value) == expected


@pytest.mark.parametrize("value,expected", [("20250101","1 Januari 2025"),("20240229","29 Februari 2024"),("20251231","31 Desember 2025"),("20250230","Tidak tersedia"),("bad","Tidak tersedia"),(None,"Tidak tersedia")])
def test_format_upload_date_is_total(value, expected):
    assert DownloaderTab.format_upload_date(value) == expected


def test_description_panel_is_read_only_plain_text(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    assert tab.description.isReadOnly()
    assert tab.description.placeholderText() == "Deskripsi tidak tersedia."
    text = "<b>bukan HTML</b> 🚀"
    tab.show_metadata({"title": "Judul", "description": text})
    qtbot.waitUntil(lambda: tab.description.toPlainText() == text)
    assert "<b>" in tab.description.toPlainText()


def test_empty_description_uses_placeholder(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    tab.show_metadata({"title": "Judul", "description": ""})
    assert tab.description.toPlainText() == ""
    assert tab.description.placeholderText() == "Deskripsi tidak tersedia."


def test_metadata_shows_complete_statistics(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    tab.show_metadata({"title":"Video", "view_count":1234567, "like_count":98765, "upload_date":"20251231"})
    text = tab.meta.text()
    assert "Views: 1.234.567" in text
    assert "Likes: 98.765" in text
    assert "Upload date: 31 Desember 2025" in text


def test_metadata_shows_fallback_for_missing_statistics(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    tab.show_metadata({"title":"Playlist"})
    assert tab.meta.text().count("Tidak tersedia") >= 3


def test_playlist_panel_shows_all_items_with_virtual_model(qtbot, tmp_path):
    tab=DownloaderTab({"download_folder":str(tmp_path)}); qtbot.addWidget(tab)
    items=tuple({"index":index+1,"title":f"Video {index+1}"} for index in range(10000))
    tab.show_metadata({"title":"Playlist","type":"playlist","playlist_items":items})
    assert tab.playlist_label.text()=="Playlist items (10.000)"
    assert not tab.playlist_view.isHidden()
    assert tab.playlist_model.rowCount()==10000
    assert tab.playlist_model.data(tab.playlist_model.index(9999))=="10000. Video 10000"


def test_empty_playlist_is_visible_but_single_video_is_hidden(qtbot, tmp_path):
    tab=DownloaderTab({"download_folder":str(tmp_path)}); qtbot.addWidget(tab)
    tab.show_metadata({"title":"Kosong","type":"playlist","playlist_items":()})
    assert not tab.playlist_label.isHidden()
    assert tab.playlist_label.text()=="Playlist items (0)"
    tab.show_metadata({"title":"Video","type":"video","playlist_items":()})
    assert tab.playlist_label.isHidden()


def test_clear_resets_and_hides_playlist(qtbot, tmp_path):
    tab=DownloaderTab({"download_folder":str(tmp_path)}); qtbot.addWidget(tab)
    tab.show_metadata({"type":"playlist","playlist_items":({"index":1,"title":"Satu"},)})
    tab.clear_form()
    assert tab.playlist_model.rowCount()==0
    assert tab.playlist_view.isHidden()


def test_playlist_selection_controls_and_count(qtbot,tmp_path):
    tab=DownloaderTab({"download_folder":str(tmp_path)}); qtbot.addWidget(tab); tab.show_metadata({"type":"playlist","playlist_items":analyzed_items()})
    assert tab.selection_count.text()=="Terpilih: 3 / 3"
    tab.playlist_model.setData(tab.playlist_model.index(1),Qt.Unchecked,Qt.CheckStateRole)
    assert tab.selected_items.isChecked(); assert not tab.all_items.isChecked() and not tab.range_enabled.isChecked(); assert tab.selection_count.text()=="Terpilih: 2 / 3"


def test_bulk_selection_buttons(qtbot,tmp_path):
    tab=DownloaderTab({"download_folder":str(tmp_path)}); qtbot.addWidget(tab); tab.show_metadata({"type":"playlist","playlist_items":analyzed_items()})
    tab.clear_selection.click(); assert tab.playlist_model.selected_count()==0
    tab.select_all.click(); assert tab.playlist_model.selected_count()==3
    tab.invert_selection.click(); assert tab.playlist_model.selected_count()==0


def test_scope_modes_are_mutually_exclusive(qtbot,tmp_path):
    tab=DownloaderTab({"download_folder":str(tmp_path)}); qtbot.addWidget(tab); tab.show_metadata({"type":"playlist","playlist_items":analyzed_items()})
    tab.selected_items.setChecked(True); assert not tab.all_items.isChecked()
    tab.range_enabled.setChecked(True); assert not tab.selected_items.isChecked()
    tab.all_items.setChecked(True); assert not tab.range_enabled.isChecked() and not tab.selected_items.isChecked()


def test_build_request_contains_compact_selected_items(qtbot,tmp_path):
    tab=DownloaderTab({"download_folder":str(tmp_path)}); qtbot.addWidget(tab); tab.url.setText("https://example.com/list"); tab.show_metadata({"type":"playlist","playlist_items":analyzed_items()})
    tab.playlist_model.setData(tab.playlist_model.index(1),Qt.Unchecked,Qt.CheckStateRole)
    request=tab.build_request()
    assert request.playlist_selection_mode=="selected"; assert request.playlist_items=="1,3"; assert request.playlist_start is None and request.playlist_end is None


def test_build_request_rejects_empty_selected_items(qtbot,tmp_path):
    tab=DownloaderTab({"download_folder":str(tmp_path)}); qtbot.addWidget(tab); tab.show_metadata({"type":"playlist","playlist_items":analyzed_items()}); tab.clear_selection.click()
    with pytest.raises(ValueError,match="Pilih minimal satu"):tab.build_request()


def test_long_description_renders_completely_in_chunks(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    text = ("αβγ\n" * 20000) + "SELESAI"
    tab.show_metadata({"title": "Panjang", "description": text})
    assert tab.description.toPlainText() != text
    qtbot.waitUntil(lambda: tab.description.toPlainText() == text, timeout=5000)


def test_new_analysis_invalidates_old_description(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    tab.show_metadata({"title": "Lama", "description": "lama" * 50000})
    tab.show_metadata({"title": "Baru", "description": "deskripsi baru"})
    qtbot.waitUntil(lambda: tab.description.toPlainText() == "deskripsi baru")
    qtbot.wait(20)
    assert tab.description.toPlainText() == "deskripsi baru"


def test_clear_stops_pending_description_render(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    tab.show_metadata({"title": "Lama", "description": "lama" * 50000})
    tab.clear_form()
    qtbot.wait(20)
    assert tab.description.toPlainText() == ""
    assert not tab._description_timer.isActive()


def test_download_mode_precedes_format_and_defaults_to_combined(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    assert tab.mode.currentText() == "Video + Audio"
    assert combo_items(tab.mode) == ["Video + Audio", "Video Only", "Audio Only"]
    form = tab.mode.parentWidget().findChild(QFormLayout)
    labels = [form.itemAt(row, QFormLayout.LabelRole).widget().text()
              for row in range(form.rowCount())
              if form.itemAt(row, QFormLayout.LabelRole)]
    assert labels.index("Mode Download") + 1 == labels.index("Format")
    assert combo_items(tab.format) == ["MP4", "WEBM", "MKV", "MOV"]
    assert combo_items(tab.quality) == ["Best", "8K", "4K", "1440p", "1080p", "720p", "480p", "360p"]


def test_download_mode_updates_and_resets_dependent_choices(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    tab.format.setCurrentText("WEBM")
    tab.quality.setCurrentText("720p")
    tab.mode.setCurrentText("Audio Only")
    assert combo_items(tab.format) == ["MP3", "M4A", "AAC", "FLAC", "WAV", "OPUS", "OGG"]
    assert combo_items(tab.quality) == ["Best", "320k", "256k", "192k", "128k"]
    assert tab.format.currentText() == "MP3"
    assert tab.quality.currentText() == "Best"
    tab.mode.setCurrentText("Video Only")
    assert combo_items(tab.format) == ["MP4", "WEBM", "MKV", "MOV"]
    assert combo_items(tab.quality) == ["Best", "8K", "4K", "1440p", "1080p", "720p", "480p", "360p"]
    assert tab.format.currentText() == "MP4"
    assert tab.quality.currentText() == "Best"


def test_audio_formats_adjust_quality_for_lossless_codecs(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    tab.mode.setCurrentText("Audio Only")
    assert combo_items(tab.format) == ["MP3", "M4A", "AAC", "FLAC", "WAV", "OPUS", "OGG"]
    assert combo_items(tab.quality) == ["Best", "320k", "256k", "192k", "128k"]
    tab.format.setCurrentText("FLAC")
    assert combo_items(tab.quality) == ["Best"]
    tab.format.setCurrentText("WAV")
    assert combo_items(tab.quality) == ["Best"]
    tab.format.setCurrentText("OPUS")
    assert combo_items(tab.quality) == ["Best", "320k", "256k", "192k", "128k"]


def test_downloader_builds_request(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path), "filename_template": "%(title)s.%(ext)s", "ffmpeg_path": ""})
    qtbot.addWidget(tab)
    tab.url.setText("https://example.com/video")
    tab.mode.setCurrentText("Audio Only")
    tab.format.setCurrentText("M4A")
    tab.quality.setCurrentText("256k")
    request = tab.build_request()
    assert request.download_mode == "Audio Only"
    assert request.format_mode == "M4A"
    assert request.quality == "256k"
    assert request.output_dir == tmp_path


def test_open_after_download_defaults_off_and_is_snapshotted(qtbot,tmp_path):
    tab=DownloaderTab({"download_folder":str(tmp_path)}); qtbot.addWidget(tab)
    assert not tab.open_after_download.isChecked()
    assert tab.build_request().open_after_download is False
    tab.open_after_download.setChecked(True); request=tab.build_request(); tab.open_after_download.setChecked(False)
    assert request.open_after_download is True


def test_all_items_and_range_controls_are_mutually_exclusive(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    assert tab.all_items.isChecked()
    assert not tab.start.isEnabled()
    tab.range_enabled.setChecked(True)
    assert not tab.all_items.isChecked()
    assert tab.start.isEnabled()
    tab.all_items.setChecked(True)
    assert not tab.range_enabled.isChecked()
    assert not tab.start.isEnabled()


def test_embed_subtitle_enables_subtitle_download(qtbot, tmp_path):
    tab = DownloaderTab({"download_folder": str(tmp_path)})
    qtbot.addWidget(tab)
    tab.embed_subtitles.setChecked(True)
    assert tab.subtitles.isChecked()


def test_logs_and_history_tabs(qtbot, tmp_path):
    logs = LogsTab(); qtbot.addWidget(logs); logs.append_log("Error", "Readable error")
    assert "Readable error" in logs.view.toPlainText()
    history = HistoryTab(HistoryService(tmp_path / "history.db")); qtbot.addWidget(history)
    assert history.table.columnCount() == 9


def test_history_tab_emits_change_after_delete(qtbot,tmp_path):
    service=HistoryService(tmp_path/"history.db"); row=service.add(HistoryEntry("Done","https://example.com")); tab=HistoryTab(service); qtbot.addWidget(tab); tab.table.selectRow(0)
    with qtbot.waitSignal(tab.history_changed):tab.delete_selected()
    assert service.get(row) is None


def test_history_tab_emits_change_after_clear(qtbot,monkeypatch,tmp_path):
    service=HistoryService(tmp_path/"history.db"); service.add(HistoryEntry("Done","https://example.com")); tab=HistoryTab(service); qtbot.addWidget(tab); monkeypatch.setattr("app.ui.history_tab.QMessageBox.question",lambda *args:QMessageBox.Yes)
    with qtbot.waitSignal(tab.history_changed):tab.clear_all()
    assert service.list()==[]


def test_log_receiver_is_registered_as_queued_qt_slot(qtbot):
    logs = LogsTab(); qtbot.addWidget(logs)
    method = logs.metaObject().indexOfSlot("append_log(QString,QString)")
    assert method >= 0
    assert logs.metaObject().method(method).methodType() == QMetaMethod.Slot


def test_main_window_has_top_tabs_and_no_sidebar(qtbot, monkeypatch, tmp_path):
    monkeypatch.setattr("app.ui.main_window.SETTINGS_PATH", tmp_path / "settings.json")
    monkeypatch.setattr("app.ui.main_window.HISTORY_PATH", tmp_path / "history.db")
    window = MainWindow(); qtbot.addWidget(window)
    assert [window.tabs.tabText(i) for i in range(window.tabs.count())] == ["Downloader", "Logs", "History"]
    assert window.findChildren(__import__("PySide6.QtWidgets", fromlist=["QDockWidget"]).QDockWidget) == []


def test_main_window_shows_installed_ytdlp_version(qtbot,monkeypatch,tmp_path):
    monkeypatch.setattr("app.ui.main_window.SETTINGS_PATH",tmp_path/"settings.json"); monkeypatch.setattr("app.ui.main_window.HISTORY_PATH",tmp_path/"history.db"); monkeypatch.setattr("app.ui.main_window.YtDlpService.installed_version",lambda:"2026.07.01")
    window=MainWindow(); qtbot.addWidget(window)
    assert window.ytdlp_version_label.text()=="yt-dlp 2026.07.01"


def test_version_status_falls_back_and_refreshes(qtbot,monkeypatch,tmp_path):
    monkeypatch.setattr("app.ui.main_window.SETTINGS_PATH",tmp_path/"settings.json"); monkeypatch.setattr("app.ui.main_window.HISTORY_PATH",tmp_path/"history.db"); versions=iter([None,"2026.07.02"]); monkeypatch.setattr("app.ui.main_window.YtDlpService.installed_version",lambda:next(versions))
    window=MainWindow(); qtbot.addWidget(window)
    assert window.ytdlp_version_label.text()=="yt-dlp tidak tersedia"
    window._update_done("updated")
    assert window.ytdlp_version_label.text()=="yt-dlp 2026.07.02"


@pytest.mark.parametrize("value,expected",[(0,"0 B"),(1024,"1,00 KB"),(1536,"1,50 KB"),(1024**3,"1,00 GB"),(1024**5,"1024,00 TB"),(None,"0 B"),(-1,"0 B"),(True,"0 B")])
def test_format_download_size_is_total(value,expected):
    assert MainWindow.format_download_size(value)==expected


def test_main_window_shows_persistent_download_totals(qtbot,monkeypatch,tmp_path):
    monkeypatch.setattr("app.ui.main_window.SETTINGS_PATH",tmp_path/"settings.json"); monkeypatch.setattr("app.ui.main_window.HISTORY_PATH",tmp_path/"history.db"); monkeypatch.setattr("app.ui.main_window.YtDlpService.installed_version",lambda:"2026.07.01")
    window=MainWindow(); qtbot.addWidget(window); row=window.history_service.add(HistoryEntry("Done","https://example.com",status="downloading")); window.history_service.complete(row,1234,1536); window.refresh_download_totals()
    assert window.download_count_label.text()=="Download selesai: 1.234 file"
    assert window.download_size_label.text()=="Total ukuran: 1,50 KB"
