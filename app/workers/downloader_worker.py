from threading import Event
import os
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot
from app.services.ytdlp_service import YtDlpService


def discover_final_paths(info):
    found=[]; seen_paths=set(); seen_containers=set(); temporary={".part",".ytdl",".temp",".tmp"}
    def add(value):
        if not isinstance(value,str) or not value.strip():return
        path=Path(value).expanduser()
        if path.suffix.lower() in temporary:return
        resolved=str(path.resolve(strict=False)); key=os.path.normcase(resolved)
        if key not in seen_paths:seen_paths.add(key); found.append(resolved)
    def visit(value):
        if isinstance(value,dict):
            identity=id(value)
            if identity in seen_containers:return
            seen_containers.add(identity); add(value.get("filepath")); add(value.get("_filename"))
            for key in ("requested_downloads","entries"):visit(value.get(key))
            moved=value.get("__files_to_move")
            if isinstance(moved,dict):
                for destination in moved.values():add(destination)
        elif isinstance(value,(list,tuple)):
            identity=id(value)
            if identity in seen_containers:return
            seen_containers.add(identity)
            for item in value:visit(item)
    visit(info)
    return tuple(found)


class _Logger:
    def __init__(self, signal): self.signal=signal
    def debug(self, msg): self.signal.emit("Debug", str(msg))
    def info(self, msg): self.signal.emit("Info", str(msg))
    def warning(self, msg): self.signal.emit("Warning", str(msg))
    def error(self, msg): self.signal.emit("Error", str(msg))


class DownloaderWorker(QObject):
    progress = Signal(dict); finished = Signal(object, dict); error = Signal(object, str); cancelled = Signal(object); log = Signal(str, str)
    def __init__(self, request, service=None): super().__init__(); self.request=request; self.service=service or YtDlpService(); self.cancel_event=Event()
    @Slot()
    def run(self):
        try:
            result=self.service.download(self.request, self.progress.emit, _Logger(self.log), self.cancel_event)
            if self.cancel_event.is_set(): self.cancelled.emit(self)
            else:
                normalized=self.service.normalize_info(result or {}); normalized["output_paths"]=discover_final_paths(result or {}); self.finished.emit(self,normalized)
        except Exception as exc:
            if self.cancel_event.is_set(): self.cancelled.emit(self)
            else: self.error.emit(self, self.service.friendly_error(exc))
    @Slot()
    def cancel(self): self.cancel_event.set()
