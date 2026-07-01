from PySide6.QtCore import QObject, Signal, Slot
from urllib.request import Request, urlopen

from app.services.ytdlp_service import YtDlpService


class AnalyzerWorker(QObject):
    finished = Signal(dict); thumbnail = Signal(bytes); error = Signal(str); log = Signal(str, str)
    def __init__(self, url: str, service=None): super().__init__(); self.url=url; self.service=service or YtDlpService()
    @Slot()
    def run(self):
        try:
            data = self.service.analyze(self.url)
            if data.get("thumbnail"):
                try:
                    request = Request(data["thumbnail"], headers={"User-Agent": "Mozilla/5.0"})
                    self.thumbnail.emit(urlopen(request, timeout=8).read())
                except Exception as exc:
                    self.log.emit("Warning", f"Thumbnail: {exc}")
            self.finished.emit(data)
        except Exception as exc: self.error.emit(self.service.friendly_error(exc))
