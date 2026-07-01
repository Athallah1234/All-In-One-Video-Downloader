import subprocess, sys
from PySide6.QtCore import QObject, Signal, Slot
from app.services.ytdlp_service import YtDlpService


class UpdaterWorker(QObject):
    finished=Signal(str); error=Signal(str); sites=Signal(list)
    def __init__(self, action="update"): super().__init__(); self.action=action
    @Slot()
    def run(self):
        try:
            if self.action=="sites": self.sites.emit(YtDlpService.list_extractors())
            else:
                result=subprocess.run([sys.executable,"-m","pip","install","--upgrade","yt-dlp"], capture_output=True, text=True, timeout=300)
                if result.returncode: raise RuntimeError(result.stderr.strip())
                self.finished.emit(result.stdout.strip())
        except Exception as exc: self.error.emit(str(exc))
