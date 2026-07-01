from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SETTINGS_PATH = DATA_DIR / "settings.json"
HISTORY_PATH = DATA_DIR / "history.db"

DEFAULT_SETTINGS = {
    "theme": "System",
    "download_folder": str(Path.home() / "Downloads"),
    "default_format": "Best video + best audio",
    "default_quality": "Best",
    "ffmpeg_path": "",
    "concurrent_downloads": 1,
    "filename_template": "%(title)s [%(id)s].%(ext)s",
    "auto_check_update": True,
    "notification_on_complete": True,
}

LIGHT_QSS = """
QWidget { background:#f5f7fb; color:#172033; font: 10pt 'Segoe UI'; }
QFrame#Card { background:white; border:1px solid #dfe5ef; border-radius:14px; }
QPushButton { background:#e9eef8; border:0; border-radius:8px; padding:8px 14px; }
QPushButton#Primary { background:#526dff; color:white; font-weight:600; }
QPushButton:disabled { background:#d6dbe5; color:#8a93a4; }
QLineEdit,QComboBox,QSpinBox,QPlainTextEdit,QTableWidget { background:white; border:1px solid #ccd4e2; border-radius:7px; padding:6px; }
QTabBar::tab { padding:10px 20px; margin:2px; border-radius:8px; }
QTabBar::tab:selected { background:#526dff; color:white; }
QProgressBar { background:#e5e9f1; border:0; border-radius:6px; text-align:center; }
QProgressBar::chunk { background:#526dff; border-radius:6px; }
"""

DARK_QSS = LIGHT_QSS.replace("#f5f7fb", "#111827").replace("#172033", "#e5e7eb").replace("background:white", "background:#1f2937").replace("#dfe5ef", "#374151").replace("#ccd4e2", "#4b5563").replace("#e9eef8", "#374151")
