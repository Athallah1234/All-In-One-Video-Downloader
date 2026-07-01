from pathlib import Path
from PySide6.QtCore import Signal,QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLineEdit,QComboBox,QPushButton,QTableWidget,QTableWidgetItem,QFileDialog,QMessageBox,QAbstractItemView


class HistoryTab(QWidget):
    redownload=Signal(str); history_changed=Signal()
    HEADERS=["Title","URL","Site","Type","Format","Quality","Output path","Status","Date/time"]
    def __init__(self, service):
        super().__init__(); self.service=service; root=QVBoxLayout(self); bar=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText("Search history..."); self.status=QComboBox(); self.status.addItems(["All","completed","failed","cancelled","downloading"]); bar.addWidget(self.search); bar.addWidget(self.status); root.addLayout(bar)
        self.table=QTableWidget(0,len(self.HEADERS)); self.table.setHorizontalHeaderLabels(self.HEADERS); self.table.setSelectionBehavior(QAbstractItemView.SelectRows); self.table.setEditTriggers(QAbstractItemView.NoEditTriggers); root.addWidget(self.table)
        actions=QHBoxLayout()
        for text,fn in [("Open file",self.open_file),("Open folder",self.open_folder),("Redownload",self.redownload_selected),("Delete selected",self.delete_selected),("Clear all",self.clear_all),("Export CSV",lambda:self.export("csv")),("Export JSON",lambda:self.export("json"))]: b=QPushButton(text); b.clicked.connect(fn); actions.addWidget(b)
        root.addLayout(actions); self.search.textChanged.connect(self.refresh); self.status.currentTextChanged.connect(self.refresh); self.refresh()
    def refresh(self):
        rows=self.service.list(self.search.text(),self.status.currentText()); self.table.setRowCount(len(rows))
        for r,item in enumerate(rows):
            values=[item.title,item.url,item.site,item.content_type,item.format,item.quality,item.output_path,item.status,item.created_at]
            for c,value in enumerate(values): cell=QTableWidgetItem(str(value)); cell.setData(256,item.id); self.table.setItem(r,c,cell)
        self.table.resizeColumnsToContents()
    def selected(self):
        row=self.table.currentRow(); return self.service.get(self.table.item(row,0).data(256)) if row>=0 else None
    def open_file(self):
        x=self.selected();
        if x and Path(x.output_path).is_file(): QDesktopServices.openUrl(QUrl.fromLocalFile(x.output_path))
    def open_folder(self):
        x=self.selected();
        if x:
            p=Path(x.output_path); QDesktopServices.openUrl(QUrl.fromLocalFile(str(p if p.is_dir() else p.parent)))
    def redownload_selected(self):
        x=self.selected();
        if x: self.redownload.emit(x.url)
    def delete_selected(self):
        x=self.selected();
        if x: self.service.delete(x.id); self.refresh(); self.history_changed.emit()
    def clear_all(self):
        if QMessageBox.question(self,"Clear history","Delete all history?")==QMessageBox.Yes: self.service.clear(); self.refresh(); self.history_changed.emit()
    def export(self,kind):
        path,_=QFileDialog.getSaveFileName(self,"Export history",f"history.{kind}",f"{kind.upper()} (*.{kind})")
        if path: getattr(self.service,f"export_{kind}")(Path(path))
