from datetime import datetime
from pathlib import Path
from PySide6.QtCore import Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QComboBox,QPushButton,QPlainTextEdit,QFileDialog


class LogsTab(QWidget):
    def __init__(self):
        super().__init__(); layout=QVBoxLayout(self); bar=QHBoxLayout(); self.level=QComboBox(); self.level.addItems(["All","Info","Warning","Error","Debug"]); self.level.currentTextChanged.connect(self._filter); bar.addWidget(self.level); bar.addStretch()
        for text,fn in [("Clear logs",self.clear),("Save logs",self.save),("Copy logs",self.copy)]: b=QPushButton(text); b.clicked.connect(fn); bar.addWidget(b)
        layout.addLayout(bar); self.view=QPlainTextEdit(); self.view.setReadOnly(True); layout.addWidget(self.view); self.records=[]
    @Slot(str, str)
    def append_log(self, level, message): self.records.append((level,f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [{level.upper()}] {message}")); self._filter()
    def _filter(self):
        chosen=self.level.currentText(); self.view.setPlainText("\n".join(text for level,text in self.records if chosen=="All" or level.lower()==chosen.lower()))
    def clear(self): self.records.clear(); self.view.clear()
    def copy(self): QGuiApplication.clipboard().setText(self.view.toPlainText())
    def save(self):
        path,_=QFileDialog.getSaveFileName(self,"Save logs","modern-video-downloader.log","Log (*.log);;Text (*.txt)")
        if path: Path(path).write_text(self.view.toPlainText(),encoding="utf-8")
