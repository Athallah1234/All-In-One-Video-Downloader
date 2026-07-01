from html import escape
import platform

import PySide6
from PySide6.QtWidgets import QMessageBox

from app import __version__
from app.services.ytdlp_service import YtDlpService


ABOUT_BODY=("<p>Downloader lintas situs berbasis extractor resmi dan generic extractor yt-dlp.</p>"
            "<p><b>Teknologi:</b> Python, PySide6, yt-dlp, FFmpeg, SQLite.</p>"
            "<p><a href='https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md'>Official supported sites</a> · "
            "<a href='https://github.com/yt-dlp/yt-dlp/wiki/FAQ'>yt-dlp FAQ</a></p>"
            "<p><b>Disclaimer:</b> Gunakan hanya untuk konten yang legal, milik sendiri, domain publik, atau memiliki izin. "
            "Pengguna bertanggung jawab mematuhi hak cipta dan Terms of Service masing-masing website.</p>")


def _display(value):
    return escape(value) if isinstance(value,str) and value else "Tidak tersedia"


def build_about_html(app_version,ytdlp_version,python_version,pyside_version):
    return (f"<h2>Modern Video Downloader {_display(app_version)}</h2>"
            f"<p><b>yt-dlp:</b> {_display(ytdlp_version)}<br>"
            f"<b>Python:</b> {_display(python_version)}<br>"
            f"<b>PySide6:</b> {_display(pyside_version)}</p>"+ABOUT_BODY)


def show_about(parent):
    text=build_about_html(__version__,YtDlpService.installed_version(),platform.python_version(),getattr(PySide6,"__version__",None))
    QMessageBox.about(parent,"About Modern Video Downloader",text)
