from pathlib import Path

from app.services.ytdlp_service import DownloadRequest
from app.workers.downloader_worker import DownloaderWorker,discover_final_paths


class SuccessfulService:
    def download(self, request, progress, logger, cancel_event):
        return {"title": "Done"}

    def normalize_info(self, result):
        return result


def test_terminal_signal_carries_worker_explicitly(qtbot, tmp_path):
    worker = DownloaderWorker(
        DownloadRequest("https://example.com/v", Path(tmp_path)),
        SuccessfulService(),
    )
    received = []
    worker.finished.connect(lambda source, data: received.append((source, data)))

    worker.run()

    assert received == [(worker, {"title": "Done", "output_paths": ()})]


def test_discover_final_paths_recurses_and_excludes_temporary_files(tmp_path):
    final=tmp_path/"final.mp3"; second=tmp_path/"second.mp4"
    info={"_filename":str(tmp_path/"source.webm.part"),"requested_downloads":[{"filepath":str(final)},{"filepath":str(final)}],"entries":[{"filepath":str(second)},None],"__files_to_move":{str(tmp_path/"old.webm"):str(final)}}
    assert discover_final_paths(info)==(str(final.resolve()),str(second.resolve()))


def test_discover_final_paths_ignores_non_strings_and_temp_suffixes(tmp_path):
    info={"filepath":123,"entries":[{"filepath":str(tmp_path/"x.tmp")},"bad"]}
    assert discover_final_paths(info)==()


def test_discover_final_paths_contains_cycles(tmp_path):
    info={"filepath":str(tmp_path/"ok.mp4")}; info["entries"]=[info]
    assert discover_final_paths(info)==(str((tmp_path/"ok.mp4").resolve()),)
