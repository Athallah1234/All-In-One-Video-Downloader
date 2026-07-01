from PySide6.QtCore import Signal
from PySide6.QtWidgets import *


class SettingsDialog(QDialog):
    update_requested=Signal()
    def __init__(self,service,parent=None):
        super().__init__(parent); self.service=service; self.setWindowTitle("Settings"); self.resize(520,560); data=service.load(); form=QFormLayout(self)
        self.theme=QComboBox(); self.theme.addItems(["System","Light","Dark"]); self.theme.setCurrentText(data["theme"]); self.folder=QLineEdit(data["download_folder"]); self.format=QComboBox(); self.format.addItems(["Best video + best audio","Video only","Audio only","MP3","M4A","MP4","WEBM"]); self.format.setCurrentText(data["default_format"]); self.quality=QComboBox(); self.quality.addItems(["Best","8K","4K","1440p","1080p","720p","480p","360p","Audio best"]); self.quality.setCurrentText(data["default_quality"]); self.ffmpeg=QLineEdit(data["ffmpeg_path"]); self.concurrent=QSpinBox(); self.concurrent.setRange(1,8); self.concurrent.setValue(data["concurrent_downloads"]); self.template=QLineEdit(data["filename_template"]); self.auto=QCheckBox(); self.auto.setChecked(data["auto_check_update"]); self.notify=QCheckBox(); self.notify.setChecked(data["notification_on_complete"])
        for label,w in [("Theme",self.theme),("Default download folder",self.folder),("Default format",self.format),("Default quality",self.quality),("FFmpeg path",self.ffmpeg),("Concurrent downloads",self.concurrent),("Filename template",self.template),("Auto check update",self.auto),("Notification on complete",self.notify)]: form.addRow(label,w)
        update=QPushButton("Update yt-dlp"); update.clicked.connect(self.update_requested); form.addRow(update); buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Reset|QDialogButtonBox.Cancel); buttons.accepted.connect(self.save); buttons.rejected.connect(self.reject); buttons.button(QDialogButtonBox.Reset).clicked.connect(self.reset); form.addRow(buttons)
    def values(self): return {"theme":self.theme.currentText(),"download_folder":self.folder.text(),"default_format":self.format.currentText(),"default_quality":self.quality.currentText(),"ffmpeg_path":self.ffmpeg.text(),"concurrent_downloads":self.concurrent.value(),"filename_template":self.template.text(),"auto_check_update":self.auto.isChecked(),"notification_on_complete":self.notify.isChecked()}
    def save(self): self.service.save(self.values()); self.accept()
    def reset(self): self.service.reset(); self.reject()
