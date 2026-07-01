# Changelog

Semua perubahan penting pada proyek **Modern Video Downloader** didokumentasikan di sini.

Format berdasarkan [Keep a Changelog](https://keepachangelog.com/id/1.0.0/),
dan proyek ini mengikuti [Semantic Versioning](https://semver.org/lang/id/).

> **Keterangan Tipe Perubahan:**
> - `Added` — Fitur baru yang ditambahkan
> - `Changed` — Perubahan pada fitur yang sudah ada
> - `Deprecated` — Fitur yang akan dihapus di versi mendatang
> - `Removed` — Fitur yang dihapus
> - `Fixed` — Perbaikan bug
> - `Security` — Perbaikan celah keamanan
> - `Performance` — Peningkatan performa
> - `Docs` — Pembaruan dokumentasi
> - `Refactor` — Perubahan kode internal tanpa perubahan perilaku
> - `Test` — Penambahan atau perbaikan unit/integration test
> - `Chore` — Pemeliharaan rutin (dependensi, tooling, CI/CD)

---

## [Unreleased]

> Fitur dan perbaikan yang sedang dalam pengembangan dan belum dirilis secara resmi.

### Planned / In Progress

- [ ] **Concurrent Downloads Queue** — Antrian unduhan paralel yang lebih canggih dengan drag-and-drop reorder
- [ ] **Thumbnail Gallery View** — Tab galeri yang menampilkan semua unduhan selesai beserta thumbnail-nya
- [ ] **Scheduled Downloads** — Jadwalkan unduhan pada waktu tertentu (misal: jam 03.00 saat traffic rendah)
- [ ] **Browser Extension Integration** — Kirim URL langsung dari ekstensi browser ke aplikasi desktop
- [ ] **SponsorBlock Integration** — Potong segmen sponsor otomatis menggunakan data komunitas SponsorBlock
- [ ] **Chapter-based Download** — Unduh hanya chapter tertentu dari video panjang
- [ ] **Subtitle Editor** — Editor subtitle inline terintegrasi
- [ ] **Batch URL Import** — Import daftar URL massal dari file `.txt` atau `.csv`
- [ ] **RSS Feed Monitoring** — Pantau feed RSS kanal dan unduh episode baru secara otomatis
- [ ] **Speed Limit Control** — Batasi kecepatan unduhan per-item atau global
- [ ] **Aria2c Integration** — Dukungan multi-connection download via aria2c sebagai alternatif engine
- [ ] **Post-processing Scripts** — Jalankan skrip kustom setelah unduhan selesai
- [ ] **Cloud Storage Upload** — Upload otomatis ke Google Drive / Dropbox / OneDrive setelah unduhan
- [ ] **Dark/Light Theme Customizer** — Editor warna tema kustom dengan preview live
- [ ] **System Tray Minimization** — Sembunyikan ke system tray saat diminimize
- [ ] **macOS Native Notification** — Dukungan notifikasi macOS Notification Center
- [ ] **Linux D-Bus Notification** — Notifikasi desktop via D-Bus untuk lingkungan Linux
- [ ] **Drag and Drop URL** — Seret-dan-lepas URL dari browser langsung ke jendela aplikasi
- [ ] **Multi-language UI** — Dukungan antarmuka multibahasa (id, en, ja, zh, dll.)

---

## [1.0.0] — 2026-07-01

> Rilis perdana publik — Modern Video Downloader lahir sebagai aplikasi desktop Python modern berfitur lengkap berbasis PySide6 + yt-dlp.

### Added — Fitur Baru

#### Antarmuka & Tema

- **Sistem tema adaptif tiga mode** — Light, Dark, dan System (mengikuti tema OS secara otomatis via `QStyleHints.colorScheme`)
- **Toggle tema instan tanpa restart** — Tombol `Theme` di header bar mengubah seluruh stylesheet QSS secara langsung
- **Layout tiga-tab bersih** — Tab `Downloader`, `Logs`, dan `History` tanpa sidebar yang memakan ruang
- **Status badge realtime di header** — Badge dengan enam status berwarna:
  - `READY` (abu-abu) — Siap menerima URL
  - `ANALYZING` (kuning) — Sedang menganalisis metadata URL
  - `DOWNLOADING` (biru) — Proses unduhan aktif
  - `COMPLETED` (hijau) — Unduhan berhasil selesai
  - `ERROR` (merah) — Terjadi kesalahan
  - `CANCELLING` (oranye) — Proses pembatalan sedang berjalan
- **Statusbar informatif** — Menampilkan: jumlah file selesai, total ukuran unduhan (diformat human-readable), dan versi yt-dlp yang terinstal
- **QSS stylesheet dual-mode** — `LIGHT_QSS` dan `DARK_QSS` yang simetris dengan warna utama `#526dff` (Indigo)
- **Font konsisten** — Seluruh UI menggunakan `Segoe UI` 10pt sebagai font default
- **Border radius modern** — Card panel `14px`, tombol `8px`, input field `7px`
- **Tombol Primary yang mencolok** — `QPushButton#Primary` dengan warna `#526dff` dan bobot font 600

#### Mode Download

- **Video + Audio** — Gabungkan stream video terbaik + audio terbaik menggunakan FFmpeg
- **Video Only** — Unduh stream video saja tanpa audio
- **Audio Only** — Ekstrak audio dengan berbagai codec (MP3, M4A, AAC, FLAC, WAV, OPUS, OGG)
- **Custom format selector** — Field teks bebas untuk memasukkan format selector yt-dlp secara manual

#### Format Video yang Didukung

| Format | Mode | Keterangan |
|--------|------|------------|
| MP4 | Video + Audio, Video Only | Merge output langsung |
| WEBM | Video + Audio, Video Only | Merge output langsung |
| MKV | Video + Audio, Video Only | Merge output langsung |
| MOV | Video + Audio, Video Only | Remux via `FFmpegVideoRemuxer` |

#### Format Audio yang Didukung

| Format | Bitrate Options | Post-processor |
|--------|----------------|----------------|
| MP3 | Best, 320k, 256k, 192k, 128k | `FFmpegExtractAudio` |
| M4A | Best | `FFmpegExtractAudio` |
| AAC | Best | `FFmpegExtractAudio` |
| FLAC | Best (lossless) | `FFmpegExtractAudio` |
| WAV | Best (lossless) | `FFmpegExtractAudio` |
| OPUS | Best | `FFmpegExtractAudio` |
| OGG | Best | `FFmpegExtractAudio` |

#### Pilihan Kualitas Video

| Kualitas | Resolusi Maksimum | Selector Fragment |
|----------|-------------------|-------------------|
| Best | Terbaik tersedia | `bestvideo+bestaudio/best` |
| 8K | 4320p | `bestvideo[height<=4320]+bestaudio` |
| 4K | 2160p | `bestvideo[height<=2160]+bestaudio` |
| 1440p | 1440p | `bestvideo[height<=1440]+bestaudio` |
| 1080p | 1080p | `bestvideo[height<=1080]+bestaudio` |
| 720p | 720p | `bestvideo[height<=720]+bestaudio` |
| 480p | 480p | `bestvideo[height<=480]+bestaudio` |
| 360p | 360p | `bestvideo[height<=360]+bestaudio` |

#### Analisis URL (Analyze URL)

- **Ekstraksi metadata lengkap** tanpa mengunduh via `yt-dlp --skip-download --extract-flat in_playlist`
- **Preview thumbnail otomatis** — Thumbnail diunduh dari URL dalam thread terpisah dan ditampilkan di panel metadata
- **Deskripsi konten bertahap (chunk-based rendering)** — Deskripsi panjang dirender secara bertahap menjaga UI tetap responsif
- **Deteksi tipe konten otomatis** dengan empat kategori:
  - `video` — Video tunggal
  - `playlist` — Playlist (berdasarkan `_type` = `playlist` atau `multi_video`)
  - `channel` — Kanal (berdasarkan nama extractor mengandung `channel`)
  - `generic` — Situs generik / tidak teridentifikasi
- **Metadata yang ditampilkan**: judul, uploader/channel, durasi, website/extractor, tipe konten, jumlah video, view count, like count, tanggal upload
- **Validasi URL** sebelum analisis — hanya skema `http://` dan `https://` yang diterima

#### Manajemen Playlist

- **Daftar item playlist** dengan tampilan: nomor indeks, judul, dan ketersediaan (availability)
- **Pilih Semua** (`Select All`) — centang semua item dalam daftar
- **Kosongkan Pilihan** (`Clear`) — hapus semua pilihan
- **Balik Pilihan** (`Invert`) — toggle pilihan: item terpilih menjadi tidak terpilih, vice versa
- **Tiga mode pemilihan item**:
  - `Download semua item` — Unduh seluruh playlist/channel
  - `Download range item` — Tentukan From (indeks awal) dan To (indeks akhir)
  - `Download item terpilih` — Pilih item spesifik dari daftar; selector otomatis dibangkitkan dalam format `"1,3,5-7"`
- **Skip unavailable videos** — `ignoreerrors=True` agar video yang dihapus/privat dalam playlist dilewati
- **Preserve structure** — Simpan file dengan hierarki folder `channel/playlist/item`
- **`QAbstractListModel` kustom** (`PlaylistItemsModel`) untuk daftar playlist yang efisien

#### Opsi Metadata dan File

| Opsi | Flag yt-dlp | Keterangan |
|------|-------------|------------|
| Embed subtitle | `embedsubtitles` | Tempelkan subtitle ke dalam container video |
| Auto subtitle | `writeautomaticsub` | Gunakan subtitle otomatis (auto-generated) dari platform |
| Subtitle languages | `subtitleslangs` | Kode bahasa: `id,en` atau `all` |
| Embed thumbnail | `embedthumbnail` + `convertthumbnails:jpg` | Sematkan sampul; thumbnail WebP/AVIF dikonversi ke JPG otomatis |
| Embed metadata | `embedmetadata` + `FFmpegMetadata` | Tambahkan metadata + chapter |
| Write info JSON | `writeinfojson` | Simpan metadata sebagai `<title>.info.json` |
| Write description | `writedescription` | Simpan deskripsi sebagai `<title>.description` |
| Write thumbnail | `writethumbnail` | Simpan thumbnail sebagai file gambar terpisah |

> **Catatan teknis:** Thumbnail WebP/AVIF secara eksplisit dikonversi ke JPG via `convertthumbnails=jpg` dan postprocessor `FFmpegThumbnailsConvertor` karena beberapa container media tidak mendukung artwork dalam format tersebut.

#### Autentikasi dan Jaringan

- **Cookies dari browser** — Dukungan tujuh browser: `Chrome`, `Firefox`, `Edge`, `Safari`, `Brave`, `Opera`, `Vivaldi` via `cookiesfrombrowser=(browser_name,)`
- **Cookies dari file** — Input `cookies.txt` format Netscape standar via `cookiefile`; divalidasi keberadaan file sebelum digunakan
- **Proxy** — Dukungan penuh: `http://`, `https://`, `socks4://`, `socks5://`, `socks5h://`; skema divalidasi sebelum dikirim ke yt-dlp

#### Progres Realtime

- **Progress bar per-item** — Persentase unduhan video/audio saat ini (diperbarui via `progress_hooks`)
- **Progress bar total** — Persentase keseluruhan playlist berdasarkan jumlah item selesai
- **Metrics real-time**: kecepatan unduhan (formatted), ETA (waktu estimasi selesai), ukuran terunduh vs total
- **Tab Logs real-time** — Setiap event yt-dlp (debug, info, warning, error) dicatat dengan timestamp dan pewarnaan berdasarkan level
- **Buka file/folder otomatis** — Setelah unduhan selesai, buka file hasil dengan aplikasi default sistem operasi

#### Riwayat Unduhan (History Tab)

- **SQLite database persisten** — Database `data/history.db` bertahan antar sesi; dibuat otomatis jika belum ada
- **Skema tabel `history`** dengan kolom lengkap:

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `id` | INTEGER PK | Primary key auto-increment |
| `title` | TEXT | Judul konten |
| `url` | TEXT | URL sumber |
| `site` | TEXT | Nama extractor/situs |
| `content_type` | TEXT | `video` / `playlist` / `channel` / `generic` |
| `format` | TEXT | Format output yang dipilih |
| `quality` | TEXT | Kualitas yang dipilih |
| `output_path` | TEXT | Path folder/file output |
| `status` | TEXT | `downloading` / `completed` / `failed` / `cancelled` |
| `created_at` | TEXT | Timestamp ISO8601 |
| `downloaded_count` | INTEGER | Jumlah item berhasil diunduh |
| `downloaded_size` | INTEGER | Total ukuran unduhan dalam bytes |

- **Migrasi otomatis (backward compatible)** — Kolom `downloaded_count` dan `downloaded_size` ditambahkan via `ALTER TABLE` jika database lama belum memilikinya
- **Filter pencarian teks** — Cari berdasarkan judul atau URL
- **Filter status** — Tampilkan semua / hanya `completed` / `failed` / `cancelled` / `downloading`
- **Aksi dari baris history**:
  - Buka file — Buka file hasil dengan aplikasi default
  - Buka folder — Buka folder output di file manager
  - Unduh ulang (Redownload) — Isi ulang form dengan parameter unduhan sebelumnya
  - Hapus baris — Hapus satu entri dari database
  - Hapus semua — Bersihkan seluruh history
- **Export history** — Export ke format **CSV** atau **JSON** untuk keperluan audit/laporan

#### Pengaturan (Settings Dialog)

| Pengaturan | Default | Tipe |
|-----------|---------|------|
| `theme` | `System` | `Light` / `Dark` / `System` |
| `download_folder` | `~/Downloads` | Path string |
| `default_format` | `Best video + best audio` | Dropdown |
| `default_quality` | `Best` | Dropdown |
| `ffmpeg_path` | (kosong) | Path string opsional |
| `concurrent_downloads` | `1` | Integer 1 hingga 8 |
| `filename_template` | `%(title)s [%(id)s].%(ext)s` | String template yt-dlp |
| `auto_check_update` | `true` | Boolean |
| `notification_on_complete` | `true` | Boolean |

- **Settings dialog** dapat dibuka dari menu/tombol di header
- **Penyimpanan atomik** (`settings_service.py`) — Tulis ke file sementara, lalu ganti secara atomik; mencegah korupsi data jika aplikasi ditutup paksa saat menyimpan
- **Reset ke default** — Tombol Reset di Settings mengembalikan semua nilai ke `DEFAULT_SETTINGS`
- **File `data/settings.json`** dibuat otomatis saat pertama kali dijalankan

#### Update yt-dlp

- **Update in-background** — Proses update yt-dlp berjalan di `UpdaterWorker` (QThread) tanpa membekukan UI
- **Versi yt-dlp** selalu ditampilkan di statusbar bawah menggunakan `importlib.metadata.version("yt-dlp")`
- **Daftar extractor aktif** dapat dilihat di dialog **Supported Sites** — memuat daftar nama dari `yt_dlp.extractor.gen_extractor_classes()`

#### Arsitektur dan Internal

- **`main.py`** — Entry point minimal: inisialisasi `QApplication`, load tema awal, tampilkan `MainWindow`
- **`app/__init__.py`** — Metadata versi: `__version__ = "1.0.0"`
- **`app/config.py`** — Konstanta path (`ROOT_DIR`, `DATA_DIR`, `SETTINGS_PATH`, `HISTORY_PATH`), `DEFAULT_SETTINGS`, `LIGHT_QSS`, `DARK_QSS`
- **`app/database.py`** — Koneksi SQLite + migrasi skema otomatis; `row_factory = sqlite3.Row` untuk akses kolom by-name
- **`YtDlpService`** — Kelas service tanpa state (stateless) sebagai abstraksi tunggal untuk semua operasi yt-dlp

| Method | Keterangan |
|--------|------------|
| `validate_url()` | Validasi skema HTTP/HTTPS |
| `analyze()` | Ekstrak metadata tanpa download |
| `normalize_info()` | Normalisasi dict info ke format internal |
| `build_options()` | Bangun opsi yt-dlp lengkap dari `DownloadRequest` |
| `download()` | Eksekusi unduhan dengan hook progress dan cancel event |
| `list_extractors()` | Daftar semua extractor aktif (sorted case-insensitive) |
| `friendly_error()` | Terjemahkan exception yt-dlp ke pesan ramah pengguna |
| `installed_version()` | Versi yt-dlp yang terinstal |

- **`DownloadRequest`** — Python `@dataclass` sebagai Data Transfer Object (DTO) yang merangkum seluruh opsi unduhan (23 field)
- **`CancelledError`** — Exception kustom yang di-raise di dalam `progress_hook` ketika `cancel_event.is_set()`
- **`QThread` Worker Pattern** via `moveToThread()`:
  - `AnalyzerWorker` — Analisis URL + fetch thumbnail di thread terpisah
  - `DownloaderWorker` — Unduhan + progress + cancel event di thread terpisah
  - `UpdaterWorker` — Update yt-dlp + daftar extractor di thread terpisah
- **`MainWindow._thread()`** — Helper factory yang membuat dan menghubungkan `QThread` secara konsisten
- **Konfirmasi keluar saat unduhan aktif** — `closeEvent` menampilkan dialog konfirmasi jika ada `DownloaderWorker` yang masih berjalan
- **Validasi playlist selector** — `_valid_playlist_selector()` memvalidasi string seperti `"1,3,5-7"` sebelum dikirim ke yt-dlp
- **Helper internal `ytdlp_service.py`**:
  - `_non_negative_int()` — Normalisasi integer non-negatif; menolak `bool`
  - `_upload_date()` — Validasi string tanggal YYYYMMDD 8-digit ASCII
  - `_playlist_item()` — Normalisasi satu entry playlist
  - `_playlist_items()` — Normalisasi seluruh entries menjadi tuple

#### Test Suite

| File Test | Yang Diuji |
|-----------|------------|
| `test_core.py` | Validasi URL, klasifikasi tipe konten, normalisasi metadata, validasi playlist selector |
| `test_ytdlp_service.py` | `build_options()`, validasi `DownloadRequest`, format selector, postprocessor |
| `test_downloader_worker.py` | Cancel event, `discover_final_paths()`, error handling |
| `test_playlist_items_model.py` | Select/clear/invert, `selected_selector()`, display data |
| `test_ui.py` | `DownloaderTab`, `HistoryTab`, komponen form, update progress |
| `test_auto_open.py` | `safe_output_files()`, `_open_completed_result()` |
| `test_about_dialog.py` | Render dialog About |

- **Framework**: `pytest >= 8.0` + `pytest-qt >= 4.4`

#### Dokumentasi

- `README.md` — Dokumentasi lengkap 900+ baris mencakup:
  - Daftar isi navigasi dengan anchor link
  - Fitur lengkap dalam format tabel
  - Panduan instalasi untuk Windows, macOS, Linux
  - Panduan instalasi FFmpeg untuk 5 platform (Windows, macOS, Ubuntu/Debian, Fedora/RHEL, Arch Linux)
  - Panduan penggunaan step-by-step untuk 7 skenario
  - Dokumentasi konfigurasi `settings.json`
  - Template nama file dan template struktur folder
  - Diagram arsitektur kode ASCII art
  - Diagram aliran data yang detail
  - Dokumentasi API komponen utama
  - Panduan troubleshooting untuk 7 masalah umum
  - Informasi data lokal dan cara reset
  - Referensi dan sumber daya
  - Panduan kontribusi
  - Klausul penggunaan legal dan etis
  - Lisensi MIT beserta tabel lisensi dependensi

#### Dependensi

| Paket | Versi Minimum | Peran |
|-------|--------------|-------|
| `PySide6` | `>= 6.7, < 7` | Framework UI Qt6 |
| `yt-dlp` | `>= 2025.1.1` | Engine unduhan video |
| `pytest` | `>= 8.0` | Framework pengujian |
| `pytest-qt` | `>= 4.4` | Plugin Qt untuk pytest |

#### Persyaratan Sistem

| Komponen | Minimum | Direkomendasikan |
|----------|---------|-----------------|
| Python | 3.11 | 3.12+ |
| OS | Windows 10 / macOS 12 / Ubuntu 20.04 | Windows 11 / macOS 14 / Ubuntu 22.04 |
| RAM | 256 MB | 512 MB+ |
| Disk | 100 MB | 200 MB+ |
| FFmpeg | Opsional | v6.x+ (wajib untuk merge/konversi) |

---

## Commit History (v1.0.0)

Berikut catatan semua commit yang membentuk rilis `v1.0.0`:

### `459a0b4` — 2026-07-01 19:18 WIB

**`docs: add MIT license section and dependency license table to README`**

- Menambahkan teks penuh lisensi MIT ke `README.md`
- Menambahkan tabel lisensi seluruh dependensi (yt-dlp, PySide6, FFmpeg, pytest, pytest-qt)
- Menambahkan catatan interpretatif lisensi MIT

---

### `670dba9` — 2026-07-01 19:12 WIB

**`docs: update repository URL and project name in installation instructions`**

- Memperbarui URL clone repositori ke `https://github.com/Athallah1234/All-In-One-Video-Downloader.git`
- Memperbarui nama direktori setelah clone di panduan instalasi

---

### `b40926e` — 2026-07-01 19:10 WIB

**`docs: add comprehensive table of contents and update internal anchor links in README.md`**

- Menambahkan Daftar Isi (Table of Contents) yang komprehensif dengan 30+ anchor link
- Memperbaiki dan menstandardisasi semua internal anchor link agar kompatibel dengan GitHub Markdown renderer

---

### `070aa3d` — 2026-07-01 19:07 WIB

**`Initial commit`**

- Inisialisasi repositori proyek **Modern Video Downloader v1.0.0**
- Seluruh kode sumber aplikasi pertama kali di-commit:

**App Core:**
- `main.py` — Entry point
- `app/__init__.py` — Versi `1.0.0`
- `app/config.py` — Konstanta dan QSS stylesheet
- `app/database.py` — SQLite + migrasi otomatis

**Services:**
- `app/services/ytdlp_service.py` — Service inti + `DownloadRequest` dataclass
- `app/services/history_service.py` — CRUD riwayat + ekspor CSV/JSON
- `app/services/settings_service.py` — Load/save/reset settings atomik
- `app/services/ffmpeg_service.py` — Deteksi FFmpeg

**Workers (QThread):**
- `app/workers/analyzer_worker.py` — AnalyzerWorker
- `app/workers/downloader_worker.py` — DownloaderWorker dengan cancel support
- `app/workers/updater_worker.py` — UpdaterWorker

**UI Components:**
- `app/ui/main_window.py` — MainWindow + orchestrator utama
- `app/ui/downloader_tab.py` — Tab utama (form, preview, progress)
- `app/ui/history_tab.py` — Tab riwayat unduhan
- `app/ui/logs_tab.py` — Tab log realtime
- `app/ui/playlist_items_model.py` — QAbstractListModel untuk playlist
- `app/ui/settings_dialog.py` — Dialog pengaturan
- `app/ui/about_dialog.py` — Dialog tentang aplikasi
- `app/ui/supported_sites_dialog.py` — Dialog daftar situs didukung

**Tests:**
- `tests/test_core.py`
- `tests/test_ytdlp_service.py`
- `tests/test_downloader_worker.py`
- `tests/test_playlist_items_model.py`
- `tests/test_ui.py`
- `tests/test_auto_open.py`
- `tests/test_about_dialog.py`

**Files lainnya:**
- `requirements.txt`
- `README.md`
- `.gitignore`

---

## Catatan Migrasi dan Kompatibilitas

### Database (`data/history.db`)

Jika Anda pernah menggunakan versi development sebelum `1.0.0`, database lama tetap kompatibel karena:

- Kolom `downloaded_count` dan `downloaded_size` ditambahkan secara otomatis via `ALTER TABLE` jika belum ada
- Tidak ada data yang hilang selama proses migrasi
- Nilai default `0` diberikan ke semua baris lama untuk kedua kolom baru tersebut

### Settings (`data/settings.json`)

- File pengaturan lama yang hanya berisi subset key tetap berfungsi normal
- Key yang tidak ditemukan dalam file akan secara otomatis diisi nilai default dari `DEFAULT_SETTINGS`
- Tidak ada perubahan nama key di `v1.0.0`

---

## Konvensi Pesan Commit

Proyek ini mengikuti konvensi [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Keterangan |
|--------|-----------|
| `feat:` | Fitur baru |
| `fix:` | Perbaikan bug |
| `docs:` | Perubahan dokumentasi saja |
| `style:` | Format kode (tidak mengubah logika) |
| `refactor:` | Refactoring tanpa perubahan perilaku |
| `perf:` | Peningkatan performa |
| `test:` | Penambahan atau perubahan test |
| `chore:` | Tugas pemeliharaan (dependensi, build) |
| `ci:` | Perubahan konfigurasi CI/CD |
| `revert:` | Membalik commit sebelumnya |

**Format commit:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Contoh:**

```
feat(downloader): add speed limit control per download item

Implement configurable per-item speed limit via yt-dlp ratelimit option.
Users can now set a maximum download speed in KB/s or MB/s from Settings.

Closes #42
```

---

## Tautan

- [Repositori GitHub](https://github.com/Athallah1234/All-In-One-Video-Downloader)
- [Laporkan Bug](https://github.com/Athallah1234/All-In-One-Video-Downloader/issues)
- [Ajukan Fitur](https://github.com/Athallah1234/All-In-One-Video-Downloader/issues/new?template=feature_request.md)
- [yt-dlp CHANGELOG](https://github.com/yt-dlp/yt-dlp/blob/master/Changelog.md)
- [PySide6 Release Notes](https://doc.qt.io/qtforpython-6/whats-new.html)

---

[Unreleased]: https://github.com/Athallah1234/All-In-One-Video-Downloader/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Athallah1234/All-In-One-Video-Downloader/releases/tag/v1.0.0
