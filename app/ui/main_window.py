from pathlib import Path
import os
from PySide6.QtCore import QThread,Slot,Qt,QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import *
from app import __version__
from app.config import SETTINGS_PATH,HISTORY_PATH,LIGHT_QSS,DARK_QSS
from app.services.settings_service import SettingsService
from app.services.history_service import HistoryService,HistoryEntry
from app.services.ytdlp_service import YtDlpService
from app.workers.analyzer_worker import AnalyzerWorker
from app.workers.downloader_worker import DownloaderWorker
from app.workers.updater_worker import UpdaterWorker
from app.ui.downloader_tab import DownloaderTab
from app.ui.logs_tab import LogsTab
from app.ui.history_tab import HistoryTab
from app.ui.settings_dialog import SettingsDialog
from app.ui.supported_sites_dialog import SupportedSitesDialog
from app.ui.about_dialog import show_about


def safe_output_files(output_dir,paths):
    root=Path(output_dir).expanduser().resolve(strict=False); found=[]; seen=set()
    for value in paths or ():
        if not isinstance(value,str) or not value.strip():continue
        candidate=Path(value).expanduser(); candidate=(root/candidate if not candidate.is_absolute() else candidate).resolve(strict=False)
        try:candidate.relative_to(root)
        except (ValueError,OSError):continue
        if not candidate.is_file():continue
        key=os.path.normcase(str(candidate))
        if key not in seen:seen.add(key); found.append(candidate)
    return tuple(found)


def completed_file_stats(paths):
    count=0; total=0; failures=0; seen=set()
    for value in paths or ():
        path=Path(value); key=os.path.normcase(str(path))
        if key in seen:continue
        seen.add(key)
        try:size=path.stat().st_size
        except (OSError,ValueError):failures+=1; continue
        if not isinstance(size,int) or isinstance(size,bool) or size<0:failures+=1; continue
        count+=1; total+=size
    return count,total,failures


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle(f"Modern Video Downloader {__version__}"); self.resize(1180,800); self.settings_service=SettingsService(SETTINGS_PATH); self.settings=self.settings_service.load(); self.history_service=HistoryService(HISTORY_PATH); self.threads=[]; self.current_worker=None; self.sites=[]; self._close_when_idle=False
        central=QWidget(); root=QVBoxLayout(central); header=QHBoxLayout(); title=QLabel("Modern Video Downloader"); title.setStyleSheet("font-size:21px;font-weight:700"); self.badge=QLabel("READY"); self.badge.setStyleSheet("background:#16a34a;color:white;border-radius:9px;padding:5px 10px;font-weight:600"); header.addWidget(title); header.addWidget(self.badge); header.addStretch()
        for text,fn in [("Theme",self.toggle_theme),("Supported Sites",self.show_sites),("Settings",self.show_settings),("About",lambda:show_about(self))]: b=QPushButton(text); b.clicked.connect(fn); header.addWidget(b)
        root.addLayout(header); self.tabs=QTabWidget(); self.downloader=DownloaderTab(self.settings); self.logs=LogsTab(); self.history=HistoryTab(self.history_service); self.tabs.addTab(self.downloader,"Downloader"); self.tabs.addTab(self.logs,"Logs"); self.tabs.addTab(self.history,"History"); root.addWidget(self.tabs); self.setCentralWidget(central)
        self.downloader.analyze_requested.connect(self.start_analyze); self.downloader.download_requested.connect(self.start_download); self.downloader.cancel_requested.connect(self.cancel); self.history.redownload.connect(self.redownload); self.history.history_changed.connect(self.refresh_download_totals); self.apply_theme(self.settings["theme"]); self.download_count_label=QLabel(); self.download_size_label=QLabel(); self.ytdlp_version_label=QLabel(); self.statusBar().addPermanentWidget(self.download_count_label); self.statusBar().addPermanentWidget(self.download_size_label); self.statusBar().addPermanentWidget(self.ytdlp_version_label); self.refresh_download_totals(); self.refresh_ytdlp_version()
    @staticmethod
    def format_download_size(value):
        if not isinstance(value,int) or isinstance(value,bool) or value<=0:return "0 B"
        size=float(value); units=("B","KB","MB","GB","TB")
        for unit in units:
            if unit=="TB" or size<1024:
                return f"{int(size)} B" if unit=="B" else f"{size:.2f} {unit}".replace(".",",")
            size/=1024
    def refresh_download_totals(self):
        count,size=self.history_service.totals(); self.download_count_label.setText(f"Download selesai: {DownloaderTab.format_count(count)} file"); self.download_size_label.setText(f"Total ukuran: {self.format_download_size(size)}")
    def refresh_ytdlp_version(self):
        version=YtDlpService.installed_version(); self.ytdlp_version_label.setText(f"yt-dlp {version}" if version else "yt-dlp tidak tersedia"); return version
    def apply_theme(self,theme):
        if theme=="System": theme="Dark" if self.palette().window().color().lightness()<128 else "Light"
        self.setStyleSheet(DARK_QSS if theme=="Dark" else LIGHT_QSS)
    def toggle_theme(self): self.apply_theme("Light" if "#111827" in self.styleSheet() else "Dark")
    def _thread(self,worker,on_finished):
        thread=QThread(self); worker.moveToThread(thread); thread.started.connect(worker.run); on_finished.connect(thread.quit); on_finished.connect(worker.deleteLater); thread.finished.connect(thread.deleteLater); thread.finished.connect(lambda:self._cleanup(thread)); self.threads.append(thread); thread.start(); return thread
    def _cleanup(self,thread):
        if thread in self.threads:self.threads.remove(thread)
        self.current_worker=None
        if self._close_when_idle and not self.threads:
            self._close_when_idle=False; self.close()
    def start_analyze(self,url):
        self.set_busy(True,"ANALYZING"); worker=AnalyzerWorker(url); self.current_worker=worker; worker.finished.connect(self.analysis_done); worker.thumbnail.connect(self.downloader.show_thumbnail_bytes); worker.error.connect(self.operation_error); worker.log.connect(self.logs.append_log); self._thread(worker,worker.finished); worker.error.connect(lambda _:self._quit_worker_thread(worker))
    def _quit_worker_thread(self,worker):
        thread=worker.thread(); thread.quit(); worker.deleteLater()
    @Slot(dict)
    def analysis_done(self,data):
        self.downloader.show_metadata(data); self.set_busy(False,"READY"); self.logs.append_log("Info",f"Analysis completed: {data.get('title')}")
    def start_download(self,request):
        try:
            if not str(request.output_dir).strip(): raise ValueError("Output folder belum dipilih.")
            request.output_dir.mkdir(parents=True,exist_ok=True)
            YtDlpService().build_options(request)
        except Exception as exc:
            self.operation_error(YtDlpService.friendly_error(exc)); return
        self.set_busy(True,"DOWNLOADING"); row=self.history_service.add(HistoryEntry(title=request.url,url=request.url,format=request.format_mode,quality=request.quality,output_path=str(request.output_dir),status="downloading")); worker=DownloaderWorker(request); worker.history_id=row; self.current_worker=worker; worker.progress.connect(self.downloader.update_progress); worker.log.connect(self.logs.append_log); worker.finished.connect(self._download_finished); worker.error.connect(self._download_failed); worker.cancelled.connect(self._download_was_cancelled); self._thread(worker,worker.finished); worker.error.connect(lambda source, _:self._quit_worker_thread(source)); worker.cancelled.connect(self._quit_worker_thread)
    @Slot(object, dict)
    def _download_finished(self,worker,data): self.download_done(worker,data)
    @Slot(object, str)
    def _download_failed(self,worker,msg): self.download_error(worker,msg)
    @Slot(object)
    def _download_was_cancelled(self,worker): self.download_cancelled(worker)
    def download_done(self,worker,data):
        files=safe_output_files(worker.request.output_dir,data.get("output_paths",())); count,size,failures=completed_file_stats(files); self.history_service.complete(worker.history_id,count,size); self.downloader.item_progress.setValue(100); self.downloader.total_progress.setValue(100); self.set_busy(False,"COMPLETED"); self.history.refresh(); self.refresh_download_totals(); self.logs.append_log("Info",f"Download completed: {data.get('title')}")
        if failures:self.logs.append_log("Warning",f"Ukuran {failures} file hasil tidak dapat dibaca.")
        self._open_completed_result(worker,data)
    def _open_completed_result(self,worker,data,opener=QDesktopServices.openUrl):
        request=worker.request
        if not request.open_after_download or self._close_when_idle:return
        files=safe_output_files(request.output_dir,data.get("output_paths",()))
        if not files:self.logs.append_log("Warning","Hasil download tidak ditemukan; tidak ada file yang dibuka."); return
        count=data.get("count"); multi=request.playlist_selection_mode in {"range","selected"} or data.get("type")=="playlist" or isinstance(count,int) and not isinstance(count,bool) and count>1
        target=Path(request.output_dir).expanduser().resolve(strict=False) if multi or len(files)>1 else files[0]
        try:opened=opener(QUrl.fromLocalFile(str(target)))
        except Exception as exc:self.logs.append_log("Warning",f"Tidak dapat membuka hasil download: {exc}"); return
        if not opened:self.logs.append_log("Warning","Tidak dapat membuka hasil download dengan aplikasi default.")
        else:self.logs.append_log("Info",f"Membuka hasil download: {target}")
    def download_error(self,worker,msg): self.history_service.update_status(worker.history_id,"failed"); self.set_busy(False,"ERROR"); self.history.refresh(); self.logs.append_log("Error",msg); QMessageBox.critical(self,"Download failed",msg)
    def download_cancelled(self,worker): self.history_service.update_status(worker.history_id,"cancelled"); self.set_busy(False,"CANCELLED"); self.history.refresh(); self.logs.append_log("Warning","Download cancelled")
    @Slot(str)
    def operation_error(self,msg): self.set_busy(False,"ERROR"); self.logs.append_log("Error",msg); QMessageBox.critical(self,"Error",msg)
    def cancel(self):
        if isinstance(self.current_worker,DownloaderWorker): self.current_worker.cancel(); self.badge.setText("CANCELLING")
    def set_busy(self,busy,status): self.downloader.set_busy(busy); self.badge.setText(status)
    def redownload(self,url): self.downloader.url.setText(url); self.tabs.setCurrentWidget(self.downloader)
    def show_settings(self):
        dialog=SettingsDialog(self.settings_service,self); dialog.update_requested.connect(self.update_ytdlp)
        if dialog.exec(): self.settings=self.settings_service.load(); self.downloader.settings=self.settings; self.apply_theme(self.settings["theme"])
    def update_ytdlp(self):
        worker=UpdaterWorker(); worker.finished.connect(self._update_done); worker.error.connect(self._update_error); self._thread(worker,worker.finished); worker.error.connect(lambda _:self._quit_worker_thread(worker))
    @Slot(str)
    def _update_done(self,text):
        self.logs.append_log("Info",text)
        if not self.refresh_ytdlp_version():self.logs.append_log("Warning","Versi yt-dlp tidak dapat dibaca setelah update.")
    @Slot(str)
    def _update_error(self,text): self.logs.append_log("Error",text)
    def show_sites(self):
        dialog=SupportedSitesDialog(self.sites,self); dialog.refresh.clicked.connect(lambda:self.load_sites(dialog)); self.load_sites(dialog); dialog.exec()
    def load_sites(self,dialog):
        worker=UpdaterWorker("sites"); worker.sites.connect(dialog.set_sites); worker.sites.connect(self._sites_loaded); worker.error.connect(self._update_error); self._thread(worker,worker.sites); worker.error.connect(lambda _:self._quit_worker_thread(worker))
    @Slot(list)
    def _sites_loaded(self,sites): self.sites=sites
    def closeEvent(self,event):
        if self.threads and QMessageBox.question(self,"Exit","A process is still running. Cancel and exit?")!=QMessageBox.Yes: event.ignore(); return
        if self.threads:
            self._close_when_idle=True; self.cancel(); self.badge.setText("CANCELLING"); event.ignore(); return
        event.accept()
