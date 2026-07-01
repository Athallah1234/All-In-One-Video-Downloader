from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Signal,Slot,Qt,QTimer
from PySide6.QtGui import QPixmap,QTextCursor
from PySide6.QtWidgets import *
from app.services.ytdlp_service import DownloadRequest,YtDlpService
from app.ui.playlist_items_model import PlaylistItemsModel


class DownloaderTab(QWidget):
    DESCRIPTION_CHUNK_SIZE=16*1024
    MONTHS_ID=("","Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember")
    analyze_requested=Signal(str); download_requested=Signal(object); cancel_requested=Signal()
    def __init__(self,settings):
        super().__init__(); self.settings=settings; outer=QVBoxLayout(self); scroll=QScrollArea(); scroll.setWidgetResizable(True); body=QWidget(); layout=QVBoxLayout(body)
        url_card=self.card("URL video, playlist, atau channel"); row=QHBoxLayout(); self.url=QLineEdit(); self.url.setPlaceholderText("https://..."); self.analyze=QPushButton("Analyze URL"); self.analyze.setObjectName("Primary"); row.addWidget(self.url,1); row.addWidget(self.analyze); url_card.layout().addLayout(row); layout.addWidget(url_card)
        split=QSplitter(Qt.Horizontal); preview=self.card("Preview metadata"); self.thumbnail=QLabel("Thumbnail"); self.thumbnail.setAlignment(Qt.AlignCenter); self.thumbnail.setMinimumHeight(170); self.meta=QLabel("Analyze URL untuk melihat metadata"); self.meta.setWordWrap(True); self.description_label=QLabel("Description"); self.description=QPlainTextEdit(); self.description.setReadOnly(True); self.description.setPlaceholderText("Deskripsi tidak tersedia."); self.description.setMinimumHeight(150); preview.layout().addWidget(self.thumbnail); preview.layout().addWidget(self.meta); preview.layout().addWidget(self.description_label); preview.layout().addWidget(self.description); self._description_text=""; self._description_offset=0; self._description_generation=0; self._description_timer=QTimer(self); self._description_timer.setInterval(0); self._description_timer.timeout.connect(self._append_description_chunk); split.addWidget(preview)
        self.playlist_label=QLabel("Playlist items (0)"); self.playlist_model=PlaylistItemsModel(self); self.playlist_view=QListView(); self.playlist_view.setModel(self.playlist_model); self.playlist_view.setUniformItemSizes(True); self.playlist_view.setMinimumHeight(180); self.selected_items=QCheckBox("Download item terpilih"); self.select_all=QPushButton("Pilih Semua"); self.clear_selection=QPushButton("Kosongkan"); self.invert_selection=QPushButton("Balik Pilihan"); self.selection_count=QLabel("Terpilih: 0 / 0"); selection_row=QHBoxLayout(); selection_row.addWidget(self.selected_items); selection_row.addWidget(self.select_all); selection_row.addWidget(self.clear_selection); selection_row.addWidget(self.invert_selection); selection_row.addWidget(self.selection_count); preview.layout().addWidget(self.playlist_label); preview.layout().addLayout(selection_row); preview.layout().addWidget(self.playlist_view); self.playlist_controls=[self.playlist_label,self.selected_items,self.select_all,self.clear_selection,self.invert_selection,self.selection_count,self.playlist_view]; [widget.hide() for widget in self.playlist_controls]; self.playlist_model.selectionChanged.connect(self._selection_count_changed); self.playlist_model.dataChanged.connect(self._playlist_selection_edited); self.select_all.clicked.connect(self.playlist_model.select_all); self.clear_selection.clicked.connect(self.playlist_model.clear_selection); self.invert_selection.clicked.connect(self.playlist_model.invert_selection); self.selected_items.toggled.connect(self._selected_items_toggled)
        opts=self.card("Download options"); form=QFormLayout(); self.mode=QComboBox(); self.mode.addItems(["Video + Audio","Video Only","Audio Only"]); self.format=QComboBox(); self.quality=QComboBox(); self.custom=QLineEdit(); self.custom.setPlaceholderText("Contoh: 137+140/22"); form.addRow("Mode Download",self.mode); form.addRow("Format",self.format); form.addRow("Quality",self.quality); form.addRow("Custom format",self.custom); self.mode.currentTextChanged.connect(self.update_download_choices); self.format.currentTextChanged.connect(self.update_quality_choices); self.update_download_choices(self.mode.currentText())
        self.subtitles=QCheckBox("Download subtitle"); self.auto_subtitles=QCheckBox("Auto subtitle"); self.embed_subtitles=QCheckBox("Embed subtitle"); self.subtitle_languages=QLineEdit("id,en"); form.addRow(self.subtitles); form.addRow(self.auto_subtitles); form.addRow("Subtitle languages",self.subtitle_languages); form.addRow(self.embed_subtitles)
        self.embed_thumbnail=QCheckBox("Embed thumbnail"); self.embed_metadata=QCheckBox("Embed metadata"); self.write_info=QCheckBox("Write info JSON"); self.write_description=QCheckBox("Write description"); self.write_thumbnail=QCheckBox("Write thumbnail");
        for w in [self.embed_thumbnail,self.embed_metadata,self.write_info,self.write_description,self.write_thumbnail]: form.addRow(w)
        self.all_items=QCheckBox("Download semua item"); self.all_items.setChecked(True); self.range_enabled=QCheckBox("Download range item"); range_row=QHBoxLayout(); self.start=QSpinBox(); self.start.setRange(1,999999); self.end=QSpinBox(); self.end.setRange(1,999999); range_row.addWidget(QLabel("From")); range_row.addWidget(self.start); range_row.addWidget(QLabel("To")); range_row.addWidget(self.end); form.addRow(self.all_items); form.addRow(self.range_enabled); form.addRow(range_row); self.start.setEnabled(False); self.end.setEnabled(False); self.range_enabled.toggled.connect(self._range_toggled); self.all_items.toggled.connect(self._all_items_toggled)
        self.open_after_download=QCheckBox("Buka hasil setelah download selesai"); self.skip=QCheckBox("Skip unavailable videos"); self.structure=QCheckBox("Simpan struktur folder playlist/channel"); form.addRow(self.open_after_download); form.addRow(self.skip); form.addRow(self.structure)
        self.browser=QComboBox(); self.browser.addItems(["None","chrome","firefox","edge","safari","brave","opera","vivaldi"]); self.cookies=QLineEdit(); cookie_btn=QPushButton("Browse"); cookie_btn.clicked.connect(self.pick_cookies); cr=QHBoxLayout(); cr.addWidget(self.cookies); cr.addWidget(cookie_btn); self.proxy=QLineEdit(); self.proxy.setPlaceholderText("http://127.0.0.1:8080"); form.addRow("Cookies browser",self.browser); form.addRow("cookies.txt",cr); form.addRow("Proxy",self.proxy)
        self.output=QLineEdit(settings.get("download_folder","")); out_btn=QPushButton("Browse"); out_btn.clicked.connect(self.pick_output); orow=QHBoxLayout(); orow.addWidget(self.output); orow.addWidget(out_btn); form.addRow("Output folder",orow); opts.layout().addLayout(form); split.addWidget(opts); split.setSizes([420,600]); layout.addWidget(split)
        progress=self.card("Realtime status"); self.item_label=QLabel("Ready"); self.item_progress=QProgressBar(); self.total_progress=QProgressBar(); self.metrics=QLabel("Speed: —  •  ETA: —  •  Size: —"); progress.layout().addWidget(self.item_label); progress.layout().addWidget(QLabel("Current item")); progress.layout().addWidget(self.item_progress); progress.layout().addWidget(QLabel("Total")); progress.layout().addWidget(self.total_progress); progress.layout().addWidget(self.metrics); layout.addWidget(progress)
        buttons=QHBoxLayout(); self.download=QPushButton("Download"); self.download.setObjectName("Primary"); self.cancel=QPushButton("Cancel"); self.clear=QPushButton("Clear"); buttons.addStretch(); buttons.addWidget(self.download); buttons.addWidget(self.cancel); buttons.addWidget(self.clear); layout.addLayout(buttons); scroll.setWidget(body); outer.addWidget(scroll)
        self.download.setEnabled(False); self.cancel.setEnabled(False); self.analyze.clicked.connect(self.request_analyze); self.download.clicked.connect(self.request_download); self.cancel.clicked.connect(self.cancel_requested); self.clear.clicked.connect(self.clear_form); self.url.textChanged.connect(lambda text:self.download.setEnabled(YtDlpService.validate_url(text))); self.embed_subtitles.toggled.connect(lambda checked:self.subtitles.setChecked(True) if checked else None)
    @staticmethod
    def card(title):
        frame=QFrame(); frame.setObjectName("Card"); box=QVBoxLayout(frame); label=QLabel(title); label.setStyleSheet("font-size:14px;font-weight:600"); box.addWidget(label); return frame
    @staticmethod
    def format_count(value):
        if not isinstance(value,int) or isinstance(value,bool) or value<0:return "Tidak tersedia"
        return f"{value:,}".replace(",",".")
    @classmethod
    def format_upload_date(cls,value):
        if not isinstance(value,str) or len(value)!=8 or not value.isascii() or not value.isdigit():return "Tidak tersedia"
        try: parsed=datetime.strptime(value,"%Y%m%d")
        except ValueError:return "Tidak tersedia"
        return f"{parsed.day} {cls.MONTHS_ID[parsed.month]} {parsed.year}"
    def pick_output(self):
        path=QFileDialog.getExistingDirectory(self,"Output folder",self.output.text());
        if path:self.output.setText(path)
    def update_download_choices(self,mode):
        self.format.blockSignals(True); self.format.clear()
        if mode=="Audio Only": self.format.addItems(["MP3","M4A","AAC","FLAC","WAV","OPUS","OGG"])
        else: self.format.addItems(["MP4","WEBM","MKV","MOV"])
        self.format.blockSignals(False); self.update_quality_choices(self.format.currentText())
    def update_quality_choices(self,format_name):
        self.quality.clear()
        if self.mode.currentText()=="Audio Only":
            choices=["Best"] if format_name in {"FLAC","WAV"} else ["Best","320k","256k","192k","128k"]
        else: choices=["Best","8K","4K","1440p","1080p","720p","480p","360p"]
        self.quality.addItems(choices)
    def _range_toggled(self,checked):
        self.start.setEnabled(checked); self.end.setEnabled(checked)
        if checked: self.all_items.setChecked(False); self.selected_items.setChecked(False)
    def _all_items_toggled(self,checked):
        if checked: self.range_enabled.setChecked(False); self.selected_items.setChecked(False)
    def _selected_items_toggled(self,checked):
        if checked:self.all_items.setChecked(False); self.range_enabled.setChecked(False)
    def _selection_count_changed(self,selected,total):self.selection_count.setText(f"Terpilih: {selected} / {total}")
    def _playlist_selection_edited(self,*_):self.selected_items.setChecked(True)
    def pick_cookies(self):
        path,_=QFileDialog.getOpenFileName(self,"Select cookies.txt","","Text (*.txt);;All files (*)");
        if path:self.cookies.setText(path)
    def request_analyze(self):
        if YtDlpService.validate_url(self.url.text()): self.analyze_requested.emit(self.url.text().strip())
        else: QMessageBox.warning(self,"Invalid URL","Masukkan URL HTTP/HTTPS yang valid.")
    def request_download(self):
        try:request=self.build_request()
        except ValueError as exc:QMessageBox.warning(self,"Pilihan playlist",str(exc)); return
        self.download_requested.emit(request)
    def build_request(self):
        scope="selected" if self.selected_items.isChecked() else ("range" if self.range_enabled.isChecked() else "all"); playlist_items=self.playlist_model.selected_selector() if scope=="selected" else ""
        if scope=="selected" and not playlist_items:raise ValueError("Pilih minimal satu video playlist.")
        return DownloadRequest(url=self.url.text().strip(),output_dir=Path(self.output.text()).expanduser(),download_mode=self.mode.currentText(),format_mode=self.format.currentText(),quality=self.quality.currentText(),custom_format=self.custom.text(),subtitles=self.subtitles.isChecked(),auto_subtitles=self.auto_subtitles.isChecked(),subtitle_languages=self.subtitle_languages.text(),embed_subtitles=self.embed_subtitles.isChecked(),embed_thumbnail=self.embed_thumbnail.isChecked(),embed_metadata=self.embed_metadata.isChecked(),write_info_json=self.write_info.isChecked(),write_description=self.write_description.isChecked(),write_thumbnail=self.write_thumbnail.isChecked(),download_all_items=self.all_items.isChecked() or scope in {"range","selected"},playlist_selection_mode=scope,playlist_items=playlist_items,playlist_start=self.start.value() if scope=="range" else None,playlist_end=self.end.value() if scope=="range" else None,open_after_download=self.open_after_download.isChecked(),skip_unavailable=self.skip.isChecked(),preserve_structure=self.structure.isChecked(),cookies_file=self.cookies.text().strip(),cookies_browser="" if self.browser.currentText()=="None" else self.browser.currentText(),proxy=self.proxy.text().strip(),filename_template=self.settings.get("filename_template","%(title)s [%(id)s].%(ext)s"),ffmpeg_path=self.settings.get("ffmpeg_path",""))
    @Slot(dict)
    def show_metadata(self,data):
        duration=data.get("duration"); dur=f"{duration//60}:{duration%60:02d}" if isinstance(duration,int) else "—"; self.meta.setText(f"<b>{data.get('title','')}</b><br>Uploader: {data.get('uploader','—')}<br>Duration: {dur}<br>Website: {data.get('extractor','—')}<br>Type: {data.get('type','—')}<br>Video count: {data.get('count') or '—'}")
        views=self.format_count(data.get("view_count")); likes=self.format_count(data.get("like_count")); upload_date=self.format_upload_date(data.get("upload_date")); self.meta.setText(self.meta.text()+f"<br>Views: {views}<br>Likes: {likes}<br>Upload date: {upload_date}")
        self._show_playlist_items(data); self._start_description_render(data.get("description",""))
    def _show_playlist_items(self,data):
        items=data.get("playlist_items"); items=items if isinstance(items,tuple) else (); self.playlist_model.set_items(items); visible=data.get("type")=="playlist" or bool(items); self.playlist_label.setText(f"Playlist items ({self.format_count(len(items))})"); [widget.setVisible(visible) for widget in self.playlist_controls]; self.all_items.setChecked(True)
    def _start_description_render(self,text):
        self._description_generation+=1; self._description_timer.stop(); self.description.clear(); self._description_text=text if isinstance(text,str) else ""; self._description_offset=0
        if self._description_text:self._description_timer.start()
    def _append_description_chunk(self):
        start=self._description_offset; end=min(start+self.DESCRIPTION_CHUNK_SIZE,len(self._description_text)); cursor=self.description.textCursor(); cursor.movePosition(QTextCursor.End); cursor.insertText(self._description_text[start:end]); self._description_offset=end
        if end>=len(self._description_text): self._description_timer.stop(); cursor.movePosition(QTextCursor.Start); self.description.setTextCursor(cursor)
    @Slot(bytes)
    def show_thumbnail_bytes(self,data):
        pix=QPixmap(); pix.loadFromData(data); self.thumbnail.setPixmap(pix.scaled(360,200,Qt.KeepAspectRatio,Qt.SmoothTransformation))
    def set_busy(self,busy): self.analyze.setEnabled(not busy); self.download.setEnabled(not busy and YtDlpService.validate_url(self.url.text())); self.cancel.setEnabled(busy); self.item_label.setText("Working..." if busy else "Ready")
    @Slot(dict)
    def update_progress(self,data):
        total=data.get("total_bytes") or data.get("total_bytes_estimate") or 0; done=data.get("downloaded_bytes") or 0; pct=int(done*100/total) if total else 0; self.item_progress.setValue(pct); idx=data.get("playlist_index") or 1; count=data.get("playlist_count") or data.get("n_entries") or 1; self.total_progress.setValue(int(((idx-1)+pct/100)*100/count)); self.item_label.setText(Path(data.get("filename") or "Downloading").name); self.metrics.setText(f"Speed: {self._size(data.get('speed'))}/s  •  ETA: {data.get('eta','—')}s  •  Size: {self._size(done)} / {self._size(total)}")
    @staticmethod
    def _size(value):
        if not value:return "—"
        for unit in ["B","KB","MB","GB"]:
            if value<1024:return f"{value:.1f} {unit}"
            value/=1024
        return f"{value:.1f} TB"
    def clear_form(self): self._show_playlist_items({}); self._start_description_render(""); self.url.clear(); self.meta.setText("Analyze URL untuk melihat metadata"); self.thumbnail.setText("Thumbnail"); self.item_progress.setValue(0); self.total_progress.setValue(0)
