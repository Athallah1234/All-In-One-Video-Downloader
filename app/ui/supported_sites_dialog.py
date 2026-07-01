from PySide6.QtCore import Slot
from PySide6.QtWidgets import *


class SupportedSitesDialog(QDialog):
    def __init__(self,sites,parent=None):
        super().__init__(parent); self.setWindowTitle("Supported Websites yt-dlp"); self.resize(600,650); layout=QVBoxLayout(self); layout.addWidget(QLabel("Daftar extractor dapat berubah karena website sering diperbarui. Percobaan extract/download adalah pemeriksaan dukungan URL yang paling valid.")); self.search=QLineEdit(); self.search.setPlaceholderText("Search extractor/site..."); self.list=QListWidget(); self.refresh=QPushButton("Refresh / update list"); layout.addWidget(self.search); layout.addWidget(self.list); layout.addWidget(self.refresh); self.sites=sites; self.search.textChanged.connect(self.filter); self.filter()
    def filter(self): self.list.clear(); q=self.search.text().lower(); self.list.addItems([x for x in self.sites if q in x.lower()])
    @Slot(list)
    def set_sites(self,sites): self.sites=sites; self.filter()
