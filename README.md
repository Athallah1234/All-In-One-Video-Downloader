<div align="center">

<h1>🎬 Modern Video Downloader</h1>

<p>
  <strong>Aplikasi desktop Python modern untuk mengunduh video, audio, playlist, dan channel dari ribuan situs web — berbasis PySide6 + yt-dlp.</strong>
</p>

<p>
  <img src="https://img.shields.io/badge/versi-1.0.0-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11%2B-yellow?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-6.7%2B-green?style=for-the-badge&logo=qt" alt="PySide6">
  <img src="https://img.shields.io/badge/yt--dlp-2025.1.1%2B-red?style=for-the-badge" alt="yt-dlp">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/lisensi-Legal%20Use%20Only-orange?style=for-the-badge" alt="License">
</p>

<p>
  <a href="#-fitur-unggulan">Fitur</a> •
  <a href="#-instalasi">Instalasi</a> •
  <a href="#-panduan-penggunaan">Panduan</a> •
  <a href="#-konfigurasi">Konfigurasi</a> •
  <a href="#-arsitektur-kode">Arsitektur</a> •
  <a href="#-troubleshooting">Troubleshooting</a> •
  <a href="#-pengujian">Pengujian</a>
</p>

</div>

---

## 📖 Tentang Proyek

**Modern Video Downloader** adalah aplikasi desktop lintas-platform yang dibangun dengan **Python 3.11+**, **PySide6** (Qt6), dan **yt-dlp** — mesin unduh video paling kuat dan aktif dikembangkan saat ini. Aplikasi ini menyediakan antarmuka grafis yang bersih, intuitif, dan penuh fitur tanpa bergantung pada Tkinter maupun sidebar navigasi yang memakan ruang.

Aplikasi mendukung **semua extractor yt-dlp** secara dinamis — artinya setiap kali yt-dlp diperbarui, situs baru yang didukung langsung tersedia tanpa perlu memperbarui aplikasi. Daftar extractor yang aktif dapat dilihat langsung dari menu **Supported Sites**.

> **Catatan penting:** Dukungan situs berubah dari waktu ke waktu bergantung pada kebijakan penyedia konten. Cara paling valid untuk memverifikasi dukungan suatu URL adalah langsung mencoba **Analyze URL** atau tombol **Download**.

---

## ✨ Fitur Unggulan

### 🖥️ Antarmuka & Tema

| Fitur | Detail |
|-------|--------|
| **Tema adaptif** | Light, Dark, dan System (otomatis mengikuti tema OS) |
| **Toggle tema instan** | Tombol **Theme** di header mengubah tampilan tanpa restart |
| **Desain tanpa sidebar** | Layout bersih dengan tiga tab: `Downloader`, `Logs`, `History` |
| **Status badge realtime** | Badge di header menampilkan status: `READY`, `ANALYZING`, `DOWNLOADING`, `COMPLETED`, `ERROR`, `CANCELLING` |
| **Statusbar informatif** | Jumlah file selesai, total ukuran unduhan, dan versi yt-dlp |

### 📥 Mode Download

| Mode | Format Tersedia | Kualitas |
|------|----------------|----------|
| **Video + Audio** | MP4, WEBM, MKV, MOV | Best, 8K, 4K, 1440p, 1080p, 720p, 480p, 360p |
| **Video Only** | MP4, WEBM, MKV, MOV | Best, 8K, 4K, 1440p, 1080p, 720p, 480p, 360p |
| **Audio Only** | MP3, M4A, AAC, FLAC, WAV, OPUS, OGG | Best, 320k, 256k, 192k, 128k |
| **Custom selector** | Format yt-dlp bebas | — |

### 🎯 Fitur Analisis URL

- **Preview metadata** sebelum mengunduh: judul, uploader, durasi, website, tipe konten (video/playlist/channel), jumlah video, views, likes, tanggal upload
- **Preview thumbnail** otomatis diunduh dan ditampilkan
- **Deskripsi konten** dirender secara bertahap (chunk-based) untuk menjaga responsivitas UI
- **Deteksi tipe konten** otomatis: `video`, `playlist`, `channel`, `generic`

### 📋 Manajemen Playlist

- Tampilan **daftar item playlist** beserta judul, indeks, dan ketersediaan
- **Pilih semua** / **Kosongkan** / **Balik pilihan** (invert selection)
- **Download range item**: tentukan From / To (contoh: item 3 sampai 10)
- **Download item terpilih**: pilih item spesifik dari daftar
- **Download semua item** (default)
- **Skip unavailable videos**: lewati video yang tidak tersedia dalam playlist
- **Preserve structure**: simpan dengan struktur folder `channel/playlist/item`

### 🎨 Opsi Metadata & File

| Opsi | Keterangan |
|------|-----------|
| `Embed subtitle` | Tempelkan subtitle ke dalam file video |
| `Auto subtitle` | Gunakan subtitle otomatis (auto-generated) |
| `Subtitle languages` | Tentukan kode bahasa, misal `id,en` atau `all` |
| `Embed thumbnail` | Sematkan sampul ke file media (konversi ke JPG otomatis) |
| `Embed metadata` | Tambahkan metadata + chapter ke file media |
| `Write info JSON` | Simpan metadata sebagai file `.info.json` |
| `Write description` | Simpan deskripsi sebagai file `.description` |
| `Write thumbnail` | Simpan thumbnail sebagai file gambar terpisah |

### 🔒 Autentikasi & Jaringan

| Opsi | Keterangan |
|------|-----------|
| **Cookies browser** | Chrome, Firefox, Edge, Safari, Brave, Opera, Vivaldi |
| **Cookies file** | Berikan `cookies.txt` format Netscape |
| **Proxy** | HTTP, HTTPS, SOCKS4, SOCKS5 |

### 📊 Progres Realtime

- **Progress bar per-item**: persentase unduhan item saat ini
- **Progress bar total**: persentase keseluruhan untuk playlist
- **Metrics**: kecepatan unduhan, ETA (perkiraan waktu selesai), ukuran terunduh vs total
- **Log realtime**: setiap event yt-dlp dicatat dengan level `Debug`, `Info`, `Warning`, `Error`
- **Buka otomatis hasil**: setelah selesai, buka file atau folder output dengan aplikasi default

### 🗂️ Riwayat Unduhan (History)

- **SQLite database** (`data/history.db`) — persisten antar sesi
- **Filter** berdasarkan teks pencarian dan status (`All`, `completed`, `failed`, `cancelled`, `downloading`)
- **Aksi dari history**: buka file, buka folder, unduh ulang (redownload), hapus baris, hapus semua
- **Export** riwayat ke **CSV** atau **JSON** untuk keperluan audit/laporan

### ⚙️ Pengaturan (Settings)

| Pengaturan | Default | Keterangan |
|-----------|---------|-----------|
| Theme | System | Light / Dark / System |
| Default download folder | `~/Downloads` | Folder keluaran default |
| Default format | Best video + best audio | Format awal saat aplikasi dibuka |
| Default quality | Best | Kualitas awal |
| FFmpeg path | *(kosong)* | Path kustom ke FFmpeg executable |
| Concurrent downloads | 1 | Jumlah unduhan paralel (1–8) |
| Filename template | `%(title)s [%(id)s].%(ext)s` | Template nama file yt-dlp |
| Auto check update | ✅ | Cek update yt-dlp otomatis |
| Notification on complete | ✅ | Notifikasi saat unduhan selesai |

### 🔄 Update yt-dlp

- Tombol **Update yt-dlp** di dalam Settings menjalankan proses update di background thread
- Versi yt-dlp terpasang selalu ditampilkan di statusbar

---

## 🖥️ Persyaratan Sistem

| Komponen | Minimum | Direkomendasikan |
|----------|---------|-----------------|
| **Python** | 3.11 | 3.12 atau lebih baru |
| **OS** | Windows 10, macOS 12, Ubuntu 20.04 | Windows 11 / macOS 14 / Ubuntu 22.04 |
| **RAM** | 256 MB | 512 MB+ |
| **Disk** | 100 MB (tanpa FFmpeg) | 200 MB+ |
| **Koneksi** | Aktif (untuk analisis & unduhan) | Broadband |
| **FFmpeg** | Opsional (wajib untuk merge/konversi) | v6.x atau lebih baru |

---

## 🚀 Instalasi

### 1. Kloning repositori

```bash
git clone https://github.com/username/modern-video-downloader.git
cd modern-video-downloader
```

### 2. Buat virtual environment

```powershell
# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instal dependensi

```bash
pip install -r requirements.txt
```

Isi `requirements.txt`:

```
PySide6>=6.7,<7
yt-dlp>=2025.1.1
pytest>=8.0
pytest-qt>=4.4
```

### 4. Jalankan aplikasi

```bash
python main.py
```

---

## 🔧 Instalasi FFmpeg

FFmpeg **wajib** untuk fitur berikut:
- Menggabungkan (merge) stream video + audio terpisah
- Konversi format (MP3, AAC, FLAC, MOV, dll.)
- Embed thumbnail & metadata ke file media
- Konversi thumbnail ke JPG agar kompatibel dengan container media

### Windows

**Cara 1 — Winget (direkomendasikan):**

```powershell
winget install Gyan.FFmpeg
```

**Cara 2 — Manual:**
1. Unduh build dari [ffmpeg.org/download.html](https://ffmpeg.org/download.html) (pilih *Windows builds from gyan.dev* atau *BtbN*)
2. Ekstrak arsip, salin folder ke lokasi yang diinginkan (misal `C:\ffmpeg`)
3. Tambahkan `C:\ffmpeg\bin` ke variabel lingkungan `PATH`
4. **Atau:** isi path FFmpeg di **Settings → FFmpeg path** (misal `C:\ffmpeg\bin\ffmpeg.exe`)

**Verifikasi:**

```powershell
ffmpeg -version
```

### macOS

```bash
brew install ffmpeg
```

### Ubuntu / Debian

```bash
sudo apt update && sudo apt install ffmpeg
```

### Fedora / RHEL

```bash
# Aktifkan RPM Fusion terlebih dahulu
sudo dnf install ffmpeg
```

### Arch Linux

```bash
sudo pacman -S ffmpeg
```

---

## 🕹️ Panduan Penggunaan

### Langkah Dasar: Download Video Tunggal

```
1. Salin URL video (YouTube, Vimeo, Twitter/X, dll.)
2. Tempel ke kolom URL di tab Downloader
3. Klik [Analyze URL] → tunggu metadata & thumbnail muncul
4. Pilih Output folder (klik Browse atau ketik path)
5. Pilih Mode: Video + Audio | Video Only | Audio Only
6. Pilih Format dan Quality
7. Klik [Download]
8. Pantau progres di progress bar dan tab Logs
9. Setelah selesai, status badge berubah menjadi COMPLETED
```

### Download Playlist / Channel

```
1. Tempel URL playlist atau channel
2. Klik [Analyze URL]
3. Daftar item playlist akan muncul secara otomatis
4. Pilih mode pilihan item:
   a. Download semua item      → centang "Download semua item"
   b. Download range item      → centang "Download range item", isi From & To
   c. Download item terpilih   → pilih item di daftar, centang "Download item terpilih"
5. Opsional: centang "Skip unavailable videos" untuk melewati video yang dihapus/privat
6. Opsional: centang "Simpan struktur folder" untuk menyusun file per channel/playlist
7. Klik [Download]
```

### Download Audio MP3

```
1. Masukkan URL
2. Analyze URL (opsional)
3. Mode: Audio Only
4. Format: MP3
5. Quality: Best atau pilih bitrate spesifik (320k, 256k, ...)
6. Klik [Download]
```

### Download dengan Custom Format Selector

Format selector menggunakan sintaks yt-dlp penuh. Contoh:

| Selector | Keterangan |
|----------|-----------|
| `bv*[height<=1080]+ba/b` | Video terbaik max 1080p + audio terbaik |
| `137+140` | Stream ID spesifik (YouTube: 1080p + m4a 128k) |
| `bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4` | MP4 terbaik |
| `worstvideo+worstaudio` | Kualitas terendah (hemat data) |
| `best[height<=720][fps<=30]` | Max 720p 30fps |

```
1. Mode: Video + Audio (atau sesuai kebutuhan)
2. Isi kolom "Custom format" dengan selector
3. Klik [Download]
```

### Login / Konten Privat / Age-Restricted

**Menggunakan cookies browser:**

```
Pilih Cookies browser → pilih browser yang sedang login
(Chrome, Firefox, Edge, Safari, Brave, Opera, Vivaldi)
```

**Menggunakan cookies.txt:**

```
1. Ekspor cookies dari browser menggunakan ekstensi "Get cookies.txt LOCALLY"
2. Simpan file cookies.txt
3. Klik Browse di kolom "cookies.txt"
4. Pilih file cookies.txt yang telah diekspor
```

### Menggunakan Proxy

```
Isi kolom Proxy dengan URL lengkap:
  HTTP:   http://127.0.0.1:8080
  HTTPS:  https://proxy.contoh.com:3128
  SOCKS5: socks5://127.0.0.1:1080
```

### Membatalkan Unduhan

```
Klik [Cancel] → badge berubah ke CANCELLING
Aplikasi membersihkan thread dengan aman sebelum berhenti
```

### Menutup Aplikasi saat Unduhan Berjalan

```
Jika ada proses berjalan, aplikasi akan meminta konfirmasi:
→ [Yes] = batalkan unduhan lalu tutup
→ [No]  = lanjutkan unduhan
```

---

## ⚙️ Konfigurasi

### File Pengaturan: `data/settings.json`

Dibuat otomatis saat aplikasi pertama kali dijalankan. Dapat diedit manual atau melalui dialog **Settings**.

```json
{
  "theme": "System",
  "download_folder": "C:/Users/nama/Downloads",
  "default_format": "Best video + best audio",
  "default_quality": "Best",
  "ffmpeg_path": "",
  "concurrent_downloads": 1,
  "filename_template": "%(title)s [%(id)s].%(ext)s",
  "auto_check_update": true,
  "notification_on_complete": true
}
```

### Template Nama File

Template menggunakan variabel yt-dlp `%(key)s`. Contoh:

| Template | Hasil |
|----------|-------|
| `%(title)s [%(id)s].%(ext)s` | `Judul Video [dQw4w9WgXcQ].mp4` *(default)* |
| `%(uploader)s - %(title)s.%(ext)s` | `Channel Name - Judul Video.mp4` |
| `%(upload_date)s %(title)s.%(ext)s` | `20240615 Judul Video.mp4` |
| `%(playlist_index)s - %(title)s.%(ext)s` | `001 - Judul Video.mp4` |

### Template Struktur Folder (Preserve Structure)

Saat "Simpan struktur folder" diaktifkan, template berubah menjadi:

```
%(channel|uploader|playlist_title|Unknown)s/
  %(playlist_title|channel|uploader|Downloads)s/
    %(playlist_index|autonumber)03d - %(title)s [%(id)s].%(ext)s
```

Contoh hasil:

```
Downloads/
  NamaChannel/
    Nama Playlist/
      001 - Judul Video Pertama [abc123].mp4
      002 - Judul Video Kedua [def456].mp4
```

---

## 🏗️ Arsitektur Kode

```
Download-Video12/
├── main.py                          # Entry point aplikasi
├── requirements.txt                 # Dependensi Python
├── data/
│   ├── settings.json                # Konfigurasi pengguna (auto-generated)
│   └── history.db                   # Database SQLite riwayat unduhan (auto-generated)
├── app/
│   ├── __init__.py                  # Versi aplikasi (__version__ = "1.0.0")
│   ├── config.py                    # Konstanta path, default settings, stylesheet QSS
│   ├── database.py                  # Koneksi & migrasi skema SQLite
│   ├── services/
│   │   ├── ytdlp_service.py         # Inti: DownloadRequest, YtDlpService
│   │   ├── history_service.py       # CRUD riwayat, ekspor CSV/JSON
│   │   ├── settings_service.py      # Load/save/reset settings.json (atomic write)
│   │   └── ffmpeg_service.py        # Deteksi FFmpeg
│   ├── workers/
│   │   ├── analyzer_worker.py       # QThread: analisis URL + fetch thumbnail
│   │   ├── downloader_worker.py     # QThread: unduhan + progress + cancel event
│   │   └── updater_worker.py        # QThread: update yt-dlp + daftar extractor
│   └── ui/
│       ├── main_window.py           # QMainWindow: orchestrator semua komponen
│       ├── downloader_tab.py        # Tab utama: form, preview, progress
│       ├── history_tab.py           # Tab riwayat: tabel, filter, aksi
│       ├── logs_tab.py              # Tab log: tampilan log realtime
│       ├── playlist_items_model.py  # QAbstractListModel untuk playlist
│       ├── settings_dialog.py       # Dialog pengaturan
│       ├── about_dialog.py          # Dialog tentang aplikasi
│       └── supported_sites_dialog.py # Dialog daftar extractor
└── tests/
    ├── test_core.py                 # Unit test logika tanpa I/O
    ├── test_ui.py                   # Pytest-Qt test komponen UI
    ├── test_ytdlp_service.py        # Test mendalam ytdlp_service
    ├── test_downloader_worker.py    # Test DownloaderWorker
    ├── test_playlist_items_model.py # Test model playlist
    ├── test_auto_open.py            # Test logika buka file otomatis
    └── test_about_dialog.py         # Test dialog About
```

### Diagram Aliran Data

```
[User Input (URL)]
       │
       ▼
[DownloaderTab] ──analyze_requested──▶ [MainWindow]
                                              │
                                              ▼
                                       [AnalyzerWorker] (QThread)
                                              │
                                       [YtDlpService.analyze()]
                                              │
                                   ┌──────────┴──────────┐
                                   ▼                      ▼
                             finished(dict)          thumbnail(bytes)
                                   │                      │
                                   ▼                      ▼
                         [MainWindow.analysis_done] [DownloaderTab.show_thumbnail_bytes]
                                   │
                         [DownloaderTab.show_metadata]
                                        │
                                        │ (User klik Download)
                                        ▼
                         [MainWindow.start_download]
                                   │
                                   ▼
                            [HistoryService.add()]   ◀── catat "downloading"
                                   │
                                   ▼
                          [DownloaderWorker] (QThread)
                                   │
                           [YtDlpService.download()]
                                   │
                       ┌───────────┼───────────┐
                       ▼           ▼            ▼
                  progress()    log()       finished() / error() / cancelled()
                       │           │            │
                       ▼           ▼            ▼
               [DownloaderTab] [LogsTab]  [HistoryService.complete()]
               update_progress  append_log  refresh_download_totals()
```

### Komponen Utama

#### `YtDlpService` — Jantung Aplikasi

Kelas service tanpa state yang membungkus yt-dlp:

| Method | Keterangan |
|--------|-----------|
| `validate_url(url)` | Validasi skema HTTP/HTTPS |
| `analyze(url)` | Ekstrak metadata tanpa mengunduh |
| `normalize_info(info)` | Normalisasi dict info yt-dlp ke format internal |
| `build_options(request)` | Bangun opsi yt-dlp dari `DownloadRequest` |
| `download(request, ...)` | Eksekusi unduhan dengan hook progress & cancel |
| `list_extractors()` | Daftar semua extractor aktif |
| `friendly_error(error)` | Pesan error yang ramah pengguna |
| `installed_version()` | Versi yt-dlp yang terinstal |

#### `DownloadRequest` — Data Transfer Object

Dataclass yang merepresentasikan seluruh opsi unduhan:

```python
@dataclass
class DownloadRequest:
    url: str
    output_dir: Path
    download_mode: str = "Video + Audio"    # "Video + Audio" | "Video Only" | "Audio Only"
    format_mode: str = "Best video + best audio"
    quality: str = "Best"                   # "Best" | "8K" | "4K" | "1440p" | ...
    custom_format: str = ""                 # Format selector kustom yt-dlp
    subtitles: bool = False
    auto_subtitles: bool = False
    subtitle_languages: str = "all"         # "id,en" atau "all"
    embed_subtitles: bool = False
    embed_thumbnail: bool = False
    embed_metadata: bool = False
    write_info_json: bool = False
    write_description: bool = False
    write_thumbnail: bool = False
    download_all_items: bool = True
    playlist_selection_mode: str = "all"    # "all" | "range" | "selected"
    playlist_items: str = ""                # "1,3,5-7" untuk mode selected
    playlist_start: int | None = None
    playlist_end: int | None = None
    open_after_download: bool = False
    skip_unavailable: bool = False
    preserve_structure: bool = False
    cookies_file: str = ""
    cookies_browser: str = ""               # "chrome" | "firefox" | ...
    proxy: str = ""                         # "http://..." | "socks5://..."
    filename_template: str = "%(title)s [%(id)s].%(ext)s"
    ffmpeg_path: str = ""
```

#### QThread Worker Pattern

Semua operasi berat dijalankan di thread terpisah menggunakan pola **moveToThread**:

```python
# Pattern yang digunakan di MainWindow._thread()
thread = QThread(self)
worker.moveToThread(thread)
thread.started.connect(worker.run)
on_finished.connect(thread.quit)
on_finished.connect(worker.deleteLater)
thread.finished.connect(thread.deleteLater)
thread.start()
```

Keunggulan: UI tidak pernah freeze selama analisis atau unduhan berlangsung.

#### Skema Database SQLite

```sql
CREATE TABLE history (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    url              TEXT NOT NULL,
    site             TEXT,
    content_type     TEXT,
    format           TEXT,
    quality          TEXT,
    output_path      TEXT,
    status           TEXT NOT NULL,  -- 'downloading' | 'completed' | 'failed' | 'cancelled'
    created_at       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    downloaded_count INTEGER NOT NULL DEFAULT 0,
    downloaded_size  INTEGER NOT NULL DEFAULT 0
);
```

Database mendukung **migrasi otomatis**: kolom `downloaded_count` dan `downloaded_size` ditambahkan via `ALTER TABLE` jika belum ada (backward compatible dengan database lama).

---

## 🧪 Pengujian

Proyek ini dilengkapi test suite menggunakan **pytest** dan **pytest-qt**.

### Menjalankan semua test

```bash
pytest
```

### Menjalankan test dengan output verbose

```bash
pytest -v
```

### Menjalankan test spesifik

```bash
# Test logika core (tanpa UI)
pytest tests/test_core.py -v

# Test layanan yt-dlp
pytest tests/test_ytdlp_service.py -v

# Test komponen UI (membutuhkan display/QApplication)
pytest tests/test_ui.py -v

# Test worker downloader
pytest tests/test_downloader_worker.py -v

# Test model playlist
pytest tests/test_playlist_items_model.py -v

# Test logika buka otomatis
pytest tests/test_auto_open.py -v

# Test dialog About
pytest tests/test_about_dialog.py -v
```

### Cakupan Test

| File Test | Yang Diuji |
|-----------|-----------|
| `test_core.py` | Validasi URL, klasifikasi info, normalisasi metadata, playlist selector |
| `test_ytdlp_service.py` | `build_options()`, validasi request, format selector, postprocessor |
| `test_downloader_worker.py` | Cancel event, discover_final_paths, error handling |
| `test_playlist_items_model.py` | Select/clear/invert, selected_selector(), display data |
| `test_ui.py` | DownloaderTab, HistoryTab, komponen form, progress update |
| `test_auto_open.py` | `safe_output_files()`, `_open_completed_result()` |
| `test_about_dialog.py` | Render dialog About |

---

## 🔍 Troubleshooting

### ❌ "Unsupported URL" atau extractor gagal

**Penyebab:** yt-dlp belum mendukung situs tersebut, atau situs telah mengubah strukturnya.

**Solusi:**
1. Buka **Settings → Update yt-dlp** untuk mendapatkan versi terbaru
2. Periksa [daftar situs yang didukung](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)
3. Cek [FAQ yt-dlp](https://github.com/yt-dlp/yt-dlp/wiki/FAQ)

---

### 🔒 Konten privat / login required / age restriction

**Penyebab:** Situs memerlukan autentikasi.

**Solusi:**
- Pilih **Cookies browser** yang sedang login ke akun (misal: Chrome dengan akun YouTube)
- Atau berikan `cookies.txt` yang diekspor dari browser

---

### ⚙️ "FFmpeg tidak ditemukan"

**Penyebab:** FFmpeg tidak terinstal atau tidak ada di `PATH`.

**Solusi:**
1. Instal FFmpeg sesuai panduan di bagian [Instalasi FFmpeg](#-instalasi-ffmpeg)
2. Verifikasi: `ffmpeg -version`
3. Jika FFmpeg ada di lokasi non-standar: isi **Settings → FFmpeg path** dengan path lengkap

---

### 🌐 Error 403, 429, atau masalah jaringan

**Penyebab:** Rate limiting, pemblokiran IP, atau koneksi bermasalah.

**Solusi:**
- Tunggu beberapa menit sebelum mencoba lagi
- Gunakan **Proxy** jika IP Anda diblokir
- Periksa koneksi internet
- Beberapa situs memerlukan cookies yang valid

> ⚠️ **Penting:** Jangan mencoba membobol atau mengakali pembatasan akses yang disengaja oleh platform.

---

### 🚫 "Permission denied"

**Penyebab:** Folder output tidak dapat ditulis.

**Solusi:**
- Pilih folder lain yang dapat ditulis (hindari `C:\Windows`, `C:\Program Files`, dll.)
- Jalankan sebagai user yang memiliki izin tulis ke folder tujuan

---

### ⏭️ Playlist berhenti di tengah jalan

**Penyebab:** Beberapa video dalam playlist tidak tersedia (dihapus/privat).

**Solusi:**
- Aktifkan **Skip unavailable videos** di opsi download

---

### 🛡️ Antivirus memblokir proses

**Penyebab:** Antivirus mendeteksi aktivitas proses yt-dlp atau FFmpeg sebagai mencurigakan (false positive).

**Solusi:**
- Tambahkan pengecualian untuk:
  - File `python.exe` / `pythonw.exe` di virtual environment
  - `yt-dlp` (package di `site-packages`)
  - Executable FFmpeg
- **Hanya lakukan ini jika instalasi berasal dari sumber tepercaya (python.org, ffmpeg.org, PyPI)**

---

### ⚡ Aplikasi tidak responsif saat download

Ini **tidak seharusnya terjadi** — semua operasi berat dijalankan di QThread terpisah. Jika terjadi:
- Pastikan versi PySide6 kompatibel: `PySide6>=6.7`
- Coba perbarui driver GPU
- Laporkan sebagai bug dengan informasi OS, versi Python, dan log error

---

## 📁 Data Lokal

Semua data runtime disimpan di folder `data/` dan **tidak disertakan dalam source control** (terdaftar di `.gitignore`):

| File | Keterangan |
|------|-----------|
| `data/settings.json` | Pengaturan pengguna (tema, folder, template, dll.) |
| `data/history.db` | Database SQLite riwayat unduhan |

**Reset pengaturan ke default:**
- Buka **Settings → tombol Reset**
- Atau hapus `data/settings.json` secara manual

**Reset riwayat:**
- Buka tab **History → Clear all**
- Atau hapus `data/history.db` secara manual

---

## 🔗 Referensi & Sumber Daya

| Sumber | Link |
|--------|------|
| yt-dlp (engine unduhan) | [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| Daftar situs didukung yt-dlp | [supportedsites.md](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) |
| Dokumentasi format selector yt-dlp | [yt-dlp FORMAT SELECTION](https://github.com/yt-dlp/yt-dlp#format-selection) |
| PySide6 (Qt for Python) | [doc.qt.io/qtforpython](https://doc.qt.io/qtforpython-6/) |
| FFmpeg | [ffmpeg.org](https://ffmpeg.org) |
| pytest-qt | [pytest-qt.readthedocs.io](https://pytest-qt.readthedocs.io) |

---

## 🤝 Kontribusi

Kontribusi sangat disambut! Berikut langkah-langkahnya:

1. **Fork** repositori ini
2. Buat branch fitur: `git checkout -b fitur/nama-fitur`
3. Commit perubahan: `git commit -m "feat: tambah fitur X"`
4. Push ke branch: `git push origin fitur/nama-fitur`
5. Buat **Pull Request**

### Panduan Kode

- Ikuti gaya kode yang sudah ada
- Tambahkan test untuk fitur baru di folder `tests/`
- Pastikan semua test lulus sebelum membuat PR: `pytest`
- Gunakan pesan commit yang deskriptif

---

## ⚖️ Penggunaan Legal & Etis

> **PERHATIAN:** Aplikasi ini hanya boleh digunakan untuk mengunduh konten yang **legal**, yaitu:
> - Konten **milik Anda sendiri**
> - Konten **domain publik**
> - Konten dengan **lisensi bebas** (Creative Commons, dsb.)
> - Konten yang **telah mendapat izin** dari pemegang hak cipta
>
> **Pengguna sepenuhnya bertanggung jawab** atas kepatuhan terhadap hak cipta, Terms of Service masing-masing platform, dan peraturan hukum yang berlaku di yurisdiksi masing-masing.
>
> Developer tidak bertanggung jawab atas penyalahgunaan aplikasi ini.

---

<div align="center">

**Modern Video Downloader v1.0.0** — Dibangun dengan ❤️ menggunakan Python, PySide6, dan yt-dlp

*Gunakan dengan bijak dan bertanggung jawab.*

</div>
