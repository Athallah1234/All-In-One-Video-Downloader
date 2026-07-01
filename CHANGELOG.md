# Changelog

Semua perubahan penting pada proyek ini didokumentasikan di file ini.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.0.0/),
dan proyek ini mengikuti [Semantic Versioning](https://semver.org/lang/id/).

---

## Daftar Isi

- [Unreleased](#unreleased)
- [1.0.0 — 2025-07-01](#100--2025-07-01)
  - [Ditambahkan](#ditambahkan)
    - [Antarmuka Pengguna](#antarmuka-pengguna-gui)
    - [Sistem Download](#sistem-download)
    - [Analisis URL & Metadata](#analisis-url--metadata)
    - [Manajemen Playlist](#manajemen-playlist)
    - [Format & Kualitas](#format--kualitas)
    - [Subtitle](#subtitle)
    - [Metadata & Thumbnail](#metadata--thumbnail)
    - [Autentikasi & Jaringan](#autentikasi--jaringan)
    - [Riwayat Unduhan](#riwayat-unduhan)
    - [Pengaturan Aplikasi](#pengaturan-aplikasi)
    - [Log & Diagnostik](#log--diagnostik)
    - [Pembaruan yt-dlp](#pembaruan-yt-dlp)
    - [Arsitektur & Internal](#arsitektur--internal)
    - [Pengujian](#pengujian)
- [Panduan Migrasi](#panduan-migrasi)
- [Versi Dependensi](#versi-dependensi)
- [Konvensi Penamaan](#konvensi-penamaan)

---

## [Unreleased]

> Bagian ini berisi perubahan yang sudah ada di branch pengembangan tetapi belum dirilis secara resmi.

### Rencana & Dalam Pengembangan

- [ ] Dukungan antrian unduhan (download queue) dengan prioritas
- [ ] Notifikasi sistem (system tray notification) saat unduhan selesai
- [ ] Preview format sebelum download (daftar stream yang tersedia)
- [ ] Pengaturan proxy per-URL
- [ ] Ekspor pengaturan dan impor konfigurasi
- [ ] Dark mode per-tab independen
- [ ] Integrasi aria2c sebagai download backend alternatif
- [ ] Tampilan statistik unduhan (grafik kecepatan, total bandwidth)
- [ ] Shortcut keyboard untuk aksi umum

---

## [1.0.0] — 2025-07-01

Rilis perdana **Modern Video Downloader v1.0.0** — aplikasi desktop lintas-platform berbasis Python, PySide6 (Qt6), dan yt-dlp untuk mengunduh video, audio, playlist, dan channel dari ribuan situs web.

---

### Ditambahkan

#### Antarmuka Pengguna (GUI)

- **Jendela utama** (`MainWindow`) berbasis `QMainWindow` dengan ukuran default 1180×800 piksel, dapat diubah ukurannya secara bebas.
- **Tiga tab utama** menggunakan `QTabWidget`:
  - `Downloader` — form input URL, opsi download, dan monitoring progres
  - `Logs` — tampilan log realtime dengan filter level
  - `History` — tabel riwayat unduhan yang dapat dicari dan diekspor
- **Header aplikasi** berisi:
  - Label judul dengan ukuran font 21px tebal
  - Badge status dinamis (`READY` / `ANALYZING` / `DOWNLOADING` / `COMPLETED` / `ERROR` / `CANCELLING`) dengan warna latar berbeda
  - Tombol **Theme**, **Supported Sites**, **Settings**, dan **About**
- **Statusbar** di bagian bawah jendela menampilkan:
  - Jumlah total file yang berhasil diunduh
  - Total ukuran kumulatif semua unduhan selesai
  - Versi yt-dlp yang sedang terinstal
- **Sistem tema** Light / Dark / System:
  - Tema `System` mendeteksi kecerahan latar sistem operasi secara otomatis
  - Toggle tema instan tanpa restart melalui tombol **Theme**
  - Stylesheet QSS terpisah untuk Light (`LIGHT_QSS`) dan Dark (`DARK_QSS`)
  - Warna aksen utama: `#526dff` (biru-ungu) untuk elemen primer
  - Tombol primer memiliki kelas `objectName("Primary")` untuk styling khusus
  - Card berbasis `QFrame` dengan `objectName("Card")`, border-radius 14px
- **Dialog Tentang** (`About`) menampilkan versi aplikasi, versi yt-dlp, versi Python, versi PySide6, deskripsi, dan tautan ke sumber daya resmi.
- **Dialog Pengaturan** (`SettingsDialog`) dengan ukuran 520×560 piksel, berisi semua opsi konfigurasi dengan tombol Save, Reset, dan Cancel.
- **Dialog Situs yang Didukung** (`SupportedSitesDialog`) dengan daftar extractor yt-dlp yang dapat dicari dan di-refresh.
- **Konfirmasi keluar** saat proses unduhan masih berjalan — dialog pilihan Cancel-and-exit atau tetap menunggu.

---

#### Sistem Download

- **Tombol Analyze URL** — menganalisis URL untuk menampilkan metadata, thumbnail, dan daftar item playlist sebelum mengunduh.
- **Tombol Download** — memulai unduhan berdasarkan semua opsi yang dipilih; diaktifkan hanya jika URL valid.
- **Tombol Cancel** — membatalkan unduhan yang sedang berjalan dengan mekanisme `threading.Event` yang aman (graceful cancellation).
- **Tombol Clear** — mengosongkan semua kolom form ke kondisi awal.
- **Progress bar per-item** (`item_progress`) — menampilkan persentase unduhan file saat ini.
- **Progress bar total** (`total_progress`) — menampilkan persentase keseluruhan untuk playlist/channel.
- **Label progres** (`item_label`) — nama file yang sedang diunduh.
- **Metrics realtime** — kecepatan unduhan (B/KB/MB/GB per detik), ETA dalam detik, ukuran terunduh vs total.
- **Buka otomatis hasil** (`open_after_download`) — setelah unduhan selesai, membuka file tunggal dengan aplikasi default, atau folder untuk playlist/multi-file.
- **Logika buka hasil yang aman** (`safe_output_files`) — memvalidasi path output berada dalam folder yang ditentukan dan file benar-benar ada.
- **Statistik file selesai** (`completed_file_stats`) — menghitung jumlah file, total ukuran, dan jumlah kegagalan stat.
- **Auto-discover path output** (`discover_final_paths`) — menelusuri seluruh struktur info dict yt-dlp (termasuk `requested_downloads`, `entries`, `__files_to_move`) untuk menemukan semua file hasil unduhan, menghindari file sementara (`.part`, `.ytdl`, `.temp`, `.tmp`).
- **Penanganan penutupan aplikasi** (`closeEvent`) — jika unduhan berjalan saat aplikasi ditutup, proses dibatalkan terlebih dahulu sebelum jendela ditutup (`_close_when_idle` flag).

---

#### Analisis URL & Metadata

- **Validasi URL** — hanya menerima URL dengan skema `http` atau `https` dan netloc yang valid.
- **Analisis tanpa unduh** — menggunakan `yt_dlp.YoutubeDL` dengan `skip_download=True` dan `extract_flat="in_playlist"` untuk mengambil metadata seefisien mungkin.
- **Normalisasi metadata** — output analisis distandarisasi ke dict internal dengan field:
  - `title` — judul konten (fallback "Tanpa judul")
  - `uploader` — nama pengunggah atau channel (fallback "-")
  - `duration` — durasi dalam detik (integer)
  - `thumbnail` — URL thumbnail
  - `extractor` — nama extractor yt-dlp
  - `type` — klasifikasi: `video`, `playlist`, `channel`, `generic`
  - `count` — jumlah item (playlist/channel)
  - `playlist_items` — tuple dict item playlist
  - `webpage_url` — URL halaman web
  - `description` — deskripsi konten
  - `view_count` — jumlah penayangan (non-negatif integer)
  - `like_count` — jumlah suka (non-negatif integer)
  - `upload_date` — tanggal upload format `YYYYMMDD`
- **Preview metadata** di UI menampilkan: judul (tebal), uploader, durasi (format M:SS), website, tipe, jumlah video, views, likes, tanggal upload (diformat dalam Bahasa Indonesia).
- **Fetch thumbnail otomatis** — thumbnail diunduh di background dengan User-Agent browser, gagal secara graceful dengan log warning jika tidak dapat diakses.
- **Render thumbnail** — ditampilkan dengan skala 360×200 piksel, mempertahankan aspek rasio dengan interpolasi smooth.
- **Render deskripsi bertahap** (chunk-based, 16 KB per chunk) menggunakan `QTimer` dengan interval 0ms — menjaga responsivitas UI saat deskripsi sangat panjang.
- **Deteksi tipe konten** otomatis:
  - `channel` — jika nama extractor mengandung kata "channel"
  - `playlist` — jika `_type` adalah `"playlist"` atau `"multi_video"`
  - `generic` — jika extractor adalah `"generic"`
  - `video` — untuk semua kasus lainnya

---

#### Manajemen Playlist

- **Tampilan daftar item** menggunakan `QListView` dengan `PlaylistItemsModel` (subclass `QAbstractListModel`).
- **Item playlist** menampilkan nomor indeks dan judul; item tidak tersedia (judul `[Video tidak tersedia]`) diberi flag `Qt.NoItemFlags` dan tidak dapat dipilih.
- **Tiga mode pemilihan item** yang saling eksklusif:
  - **Download semua item** (`playlist_selection_mode="all"`) — default, mengunduh seluruh playlist
  - **Download range item** (`playlist_selection_mode="range"`) — isi From dan To; menggunakan `playliststart` dan `playlistend` yt-dlp
  - **Download item terpilih** (`playlist_selection_mode="selected"`) — pilih item individual dari daftar; menggunakan `playlist_items` yt-dlp
- **Tombol aksi playlist**:
  - **Pilih Semua** — mencentang semua item yang tersedia
  - **Kosongkan** — menghapus centang semua item
  - **Balik Pilihan** — membalik status centang setiap item
- **Counter pilihan** realtime menampilkan "Terpilih: X / Y" (X item terpilih dari Y item yang dapat dipilih).
- **Selector string** (`selected_selector()`) — mengonversi item terpilih ke format range yt-dlp (contoh: `"1-3,5,8-9"`) dengan penggabungan range yang berurutan secara otomatis.
- **Validasi selector** (`_valid_playlist_selector`) — memastikan format selector valid sebelum dikirim ke yt-dlp.
- **Sinkronisasi mode** — memilih item di daftar otomatis mengaktifkan mode "Download item terpilih".
- **Skip unavailable videos** — mengaktifkan `ignoreerrors=True` di yt-dlp untuk melewati video yang tidak tersedia.
- **Preserve structure** — menggunakan template folder bertingkat `channel/playlist/item` untuk menyimpan file dengan hierarki direktori yang mencerminkan struktur konten.
- **Kontrol playlist tersembunyi** secara default — daftar dan kontrol pilihan hanya ditampilkan jika konten yang dianalisis adalah playlist atau channel.

---

#### Format & Kualitas

- **Tiga mode download**:
  - `Video + Audio` — menggabungkan stream video terbaik dan audio terbaik (default)
  - `Video Only` — hanya stream video tanpa audio
  - `Audio Only` — hanya stream audio, dengan konversi via FFmpeg
- **Format video**: MP4, WEBM, MKV, MOV
- **Format audio**: MP3, M4A, AAC, FLAC, WAV, OPUS, OGG
- **Kualitas video**: Best, 8K (4320p), 4K (2160p), 1440p, 1080p, 720p, 480p, 360p
- **Kualitas audio**: Best, 320k, 256k, 192k, 128k; format lossless (FLAC, WAV) selalu menggunakan best
- **Custom format selector** — mendukung sintaks format yt-dlp penuh, contoh: `bv*[height<=1080]+ba/b`
- **Format selector otomatis**:
  - `Video + Audio` dengan quality limit: `bestvideo[height<=N]+bestaudio/best[height<=N]/best`
  - `Video Only` dengan quality limit: `bestvideo[height<=N]/bestvideo`
  - `Audio Only`: `bestaudio/best`
  - Custom format mengambil alih semua selector di atas
- **Merge output format** — container target (`mp4`, `webm`, `mkv`) diteruskan sebagai `merge_output_format`
- **MOV remux** — menggunakan `FFmpegVideoRemuxer` postprocessor karena MOV tidak didukung sebagai merge target langsung
- **Audio extraction** — menggunakan `FFmpegExtractAudio` postprocessor; bitrate diekstrak dari string quality (contoh: `"192k"` → `"192"`)
- **Update pilihan format dan kualitas** secara dinamis saat mode download berubah

---

#### Subtitle

- **Download subtitle** (`writesubtitles`) — mengunduh file subtitle terpisah
- **Subtitle otomatis** (`writeautomaticsub`) — menggunakan subtitle auto-generated (misal dari YouTube)
- **Embed subtitle** (`embedsubtitles`) — menyematkan subtitle ke dalam file video; tidak berlaku untuk format audio
- **Bahasa subtitle** (`subtitleslangs`) — daftar kode bahasa dipisahkan koma (contoh: `id,en`); default `all`
- **Sinkronisasi embed** — mengaktifkan embed subtitle juga otomatis mengaktifkan opsi download subtitle

---

#### Metadata & Thumbnail

- **Embed thumbnail** (`embedthumbnail`) — menyematkan gambar sampul ke dalam file media
- **Konversi thumbnail ke JPG** (`convertthumbnails="jpg"`) — thumbnail WebP/AVIF dikonversi ke JPEG sebelum di-embed agar kompatibel dengan container video dan audio
- **Urutan postprocessor thumbnail** yang benar: `FFmpegThumbnailsConvertorPP` → `EmbedThumbnailPP`
- **Embed metadata** (`embedmetadata`) — menyematkan judul, artis, album, dan chapter ke file media menggunakan `FFmpegMetadataPP`
- **Write info JSON** (`writeinfojson`) — menyimpan seluruh metadata sebagai file `.info.json`
- **Write description** (`writedescription`) — menyimpan deskripsi konten sebagai file `.description`
- **Write thumbnail** (`writethumbnail`) — menyimpan gambar sampul sebagai file gambar terpisah

---

#### Autentikasi & Jaringan

- **Cookies dari browser** (`cookiesfrombrowser`) — mendukung Chrome, Firefox, Edge, Safari, Brave, Opera, Vivaldi
- **Cookies dari file** (`cookiefile`) — menerima file `cookies.txt` format Netscape; divalidasi keberadaannya sebelum digunakan
- **Proxy** (`proxy`) — mendukung HTTP, HTTPS, SOCKS4, SOCKS5 (`socks5h`); divalidasi skema URL sebelum digunakan
- **Validasi proxy** — menolak URL proxy tanpa skema yang valid (misal `localhost:8080` tanpa `http://`)
- **Retry otomatis** — `retries=10`, `fragment_retries=10`, `file_access_retries=5`, `extractor_retries=5`
- **Continue download** — `continuedl=True` memungkinkan melanjutkan unduhan yang terputus
- **Safe Windows filenames** — `windowsfilenames=True` diaktifkan otomatis di Windows untuk mengganti karakter yang tidak valid

---

#### Riwayat Unduhan

- **Database SQLite** tersimpan di `data/history.db` — persisten antar sesi aplikasi
- **Skema tabel** `history` dengan kolom:
  - `id` — primary key auto-increment
  - `title`, `url` — identitas konten
  - `site`, `content_type` — sumber dan jenis konten
  - `format`, `quality` — format dan kualitas yang diunduh
  - `output_path` — path folder/file keluaran
  - `status` — status unduhan: `downloading`, `completed`, `failed`, `cancelled`
  - `created_at` — timestamp ISO 8601
  - `downloaded_count` — jumlah file yang berhasil diunduh
  - `downloaded_size` — total ukuran file dalam byte
- **Migrasi otomatis** — kolom `downloaded_count` dan `downloaded_size` ditambahkan via `ALTER TABLE` jika belum ada (backward compatible dengan database dari versi sebelumnya)
- **Pencatatan otomatis** — setiap unduhan dicatat saat dimulai dan diperbarui saat selesai/gagal/dibatalkan
- **Filter riwayat** berdasarkan teks pencarian (title/URL) dan status
- **Aksi dari tab History**:
  - **Open file** — membuka file hasil unduhan dengan aplikasi default OS
  - **Open folder** — membuka folder output di file manager
  - **Redownload** — mengisi kembali URL di tab Downloader
  - **Delete selected** — menghapus satu baris dari riwayat
  - **Clear all** — menghapus seluruh riwayat (dengan konfirmasi)
- **Export CSV** — mengekspor seluruh riwayat ke file `.csv` dengan encoding UTF-8 BOM
- **Export JSON** — mengekspor seluruh riwayat ke file `.json` dengan indentasi dan karakter non-ASCII dipertahankan
- **Statistik kumulatif** di statusbar — total file selesai dan total ukuran dari semua unduhan `completed`

---

#### Pengaturan Aplikasi

- **Penyimpanan pengaturan** di `data/settings.json` menggunakan `SettingsService`
- **Atomic write** — pengaturan ditulis ke file sementara (`.tmp`) lalu di-rename untuk mencegah korupsi file saat proses tulis terganggu
- **Pemulihan file rusak** — jika `settings.json` tidak dapat diparsing, file diganti nama menjadi `.broken` dan nilai default digunakan
- **Nilai pengaturan default**:
  - `theme`: `"System"` — mengikuti tema OS
  - `download_folder`: `~/Downloads` — folder unduhan default
  - `default_format`: `"Best video + best audio"` — format awal
  - `default_quality`: `"Best"` — kualitas awal
  - `ffmpeg_path`: `""` — path FFmpeg kustom (kosong = otomatis via `PATH`)
  - `concurrent_downloads`: `1` — unduhan paralel (1–8)
  - `filename_template`: `"%(title)s [%(id)s].%(ext)s"` — template nama file yt-dlp
  - `auto_check_update`: `true` — cek update yt-dlp otomatis
  - `notification_on_complete`: `true` — notifikasi saat selesai
- **Resolusi FFmpeg** (`FFmpegService.resolve()`) — menerima path file atau direktori; jika direktori, mencari `ffmpeg.exe` (Windows) atau `ffmpeg` (POSIX); fallback ke `shutil.which("ffmpeg")`
- **Reset pengaturan** — mengembalikan semua nilai ke default via tombol Reset di dialog

---

#### Log & Diagnostik

- **Tab Logs** dengan `QPlainTextEdit` (read-only) menampilkan semua event dari yt-dlp secara realtime
- **Format baris log**: `[YYYY-MM-DD HH:MM:SS] [LEVEL] Pesan`
- **Level log**: `Debug`, `Info`, `Warning`, `Error`
- **Filter level log** — dropdown untuk menampilkan level tertentu atau semua level
- **Aksi log**:
  - **Clear logs** — menghapus seluruh tampilan dan rekaman log
  - **Save logs** — menyimpan log ke file `.log` atau `.txt`
  - **Copy logs** — menyalin semua log ke clipboard sistem
- **Logger custom** (`_Logger`) — menjembatani interface logger yt-dlp (`debug`, `info`, `warning`, `error`) ke sinyal Qt `log(str, str)`

---

#### Pembaruan yt-dlp

- **Tombol Update yt-dlp** di dialog Settings menjalankan `pip install --upgrade yt-dlp` di background thread
- **UpdaterWorker** dengan dua mode aksi:
  - `"update"` — memperbarui yt-dlp via pip (timeout 300 detik)
  - `"sites"` — memuat daftar extractor aktif dari yt-dlp yang terinstal
- **Pembaruan versi di statusbar** — versi yt-dlp diperbarui otomatis setelah update selesai
- **Dialog Supported Sites** — menampilkan daftar semua nama extractor yang dapat dicari, dengan tombol Refresh untuk memperbarui daftar dari yt-dlp yang baru

---

#### Arsitektur & Internal

- **Pola QThread Worker** — semua operasi I/O berat (analisis URL, unduhan, update pip, list extractor) dijalankan di QThread terpisah menggunakan `moveToThread`, menjaga UI tetap responsif
- **Lifecycle thread yang aman** — sinyal `on_finished` terhubung ke `thread.quit()` dan `worker.deleteLater()`; `thread.finished` terhubung ke `thread.deleteLater()` dan cleanup list thread
- **Cancel event berbasis `threading.Event`** — unduhan dapat dibatalkan kapan saja dari thread UI; event diperiksa di dalam progress hook yt-dlp
- **Graceful close** — jika ada thread berjalan saat aplikasi ditutup, unduhan dibatalkan terlebih dahulu (`_close_when_idle=True`) sebelum jendela ditutup
- **Signal-slot yang diketik** — semua koneksi sinyal menggunakan tipe eksplisit (`Signal(dict)`, `Signal(object, str)`, dll.) untuk keamanan runtime
- **`DownloadRequest` dataclass** — merepresentasikan seluruh parameter unduhan sebagai objek yang dapat diinspeksi dan diuji
- **`YtDlpService` stateless** — tidak menyimpan state; dapat diinstansiasi berulang kali tanpa efek samping
- **Pesan error yang ramah pengguna** (`friendly_error()`) — mengonversi exception teknis ke pesan Bahasa Indonesia yang mudah dipahami
- **Pemisahan lapisan** yang jelas: `services/` (logika bisnis), `workers/` (threading), `ui/` (presentasi)
- **Injeksi dependensi di worker** — `service` parameter opsional di worker memungkinkan mock di unit test
- **SQLite Row factory** — `connection.row_factory = sqlite3.Row` memungkinkan akses kolom by-name
- **Path safety** — semua path output divalidasi berada dalam direktori yang ditentukan (`safe_output_files` menggunakan `path.relative_to(root)`)
- **Penanganan path Windows** — `os.path.normcase()` digunakan untuk deduplication path case-insensitive di Windows

---

#### Pengujian

- **Framework**: pytest ≥ 8.0 + pytest-qt ≥ 4.4
- **7 file test** dengan total lebih dari 100 kasus uji:

| File | Fokus Pengujian |
|------|----------------|
| `test_core.py` | Validasi URL, klasifikasi info, normalisasi metadata, playlist selector |
| `test_ytdlp_service.py` | `build_options()`, format selector, postprocessor, validasi request, edge case |
| `test_downloader_worker.py` | Cancel event, `discover_final_paths()`, error handling |
| `test_playlist_items_model.py` | Select/clear/invert, `selected_selector()`, item tidak tersedia |
| `test_ui.py` | DownloaderTab form, HistoryTab, `update_progress()`, interaksi widget |
| `test_auto_open.py` | `safe_output_files()`, `_open_completed_result()`, logika multi vs single file |
| `test_about_dialog.py` | Render `build_about_html()`, sanitasi HTML dengan `escape()` |

- **Pendekatan pengujian**:
  - `monkeypatch` untuk mengisolasi dependensi eksternal (metadata, subprocess)
  - `tmp_path` fixture pytest untuk pengujian I/O tanpa side effect
  - `@pytest.mark.parametrize` untuk pengujian berbasis data dengan banyak kasus input
  - Pengujian integrasi `yt_dlp.YoutubeDL` nyata untuk verifikasi postprocessor pipeline
  - Mock `service` di worker untuk pengujian unit tanpa yt-dlp aktif

---

### Diubah

> Versi ini adalah rilis perdana — tidak ada perubahan dari versi sebelumnya.

---

### Diperbaiki

> Versi ini adalah rilis perdana — tidak ada perbaikan bug dari versi sebelumnya.

---

### Dihapus

> Versi ini adalah rilis perdana — tidak ada fitur yang dihapus.

---

### Keamanan

- **Validasi path output** — path file hasil unduhan diverifikasi berada dalam direktori output yang ditentukan pengguna untuk mencegah path traversal
- **Validasi URL** — hanya URL HTTP/HTTPS yang diterima; URL dengan skema lain (`file://`, `ftp://`, dll.) ditolak
- **Validasi cookies file** — path file cookies diverifikasi keberadaannya sebelum diteruskan ke yt-dlp
- **Validasi proxy URL** — skema proxy diverifikasi terhadap daftar izin (`http`, `https`, `socks4`, `socks5`, `socks5h`)
- **Validasi playlist selector** — format selector divalidasi dengan aturan ketat sebelum diteruskan ke yt-dlp
- **Disclaimer penggunaan legal** — peringatan hak cipta ditampilkan di dialog About dan README

---

## Panduan Migrasi

### Dari versi sebelumnya (pre-1.0.0)

Jika Anda menggunakan versi pengembangan sebelum rilis ini, perhatikan hal berikut:

**Database `history.db`:**
Skema database mengalami penambahan dua kolom baru secara otomatis saat aplikasi pertama kali dijalankan:
```sql
ALTER TABLE history ADD COLUMN downloaded_count INTEGER NOT NULL DEFAULT 0;
ALTER TABLE history ADD COLUMN downloaded_size INTEGER NOT NULL DEFAULT 0;
```
Tidak perlu tindakan manual — migrasi dilakukan otomatis.

**File `settings.json`:**
Jika `settings.json` dari versi lama tidak mengandung kunci baru, nilai default akan digunakan secara otomatis.
Untuk menggunakan nilai default sepenuhnya, hapus `data/settings.json` atau klik **Reset** di dialog Settings.

---

## Versi Dependensi

| Paket | Versi Minimum | Versi Diuji | Catatan |
|-------|--------------|-------------|---------|
| Python | 3.11 | 3.12.x | `int \| None` union type syntax memerlukan Python ≥ 3.10 |
| PySide6 | 6.7.0 | 6.7.x | Qt6 binding resmi untuk Python |
| yt-dlp | 2025.1.1 | 2025.x | Engine unduhan utama |
| pytest | 8.0.0 | 8.x | Framework pengujian |
| pytest-qt | 4.4.0 | 4.4.x | Plugin Qt untuk pytest |
| FFmpeg | 4.0 (opsional) | 6.x, 7.x | Wajib untuk merge, konversi, embed |
| SQLite | 3.x (bawaan Python) | — | Database riwayat unduhan |

---

## Konvensi Penamaan

Changelog ini menggunakan kategori berikut sesuai Keep a Changelog:

| Kategori | Keterangan |
|----------|-----------|
| `Ditambahkan` | Fitur baru yang ditambahkan |
| `Diubah` | Perubahan pada fitur yang sudah ada |
| `Deprecated` | Fitur yang akan dihapus di versi mendatang |
| `Dihapus` | Fitur yang dihapus dari versi ini |
| `Diperbaiki` | Perbaikan bug |
| `Keamanan` | Perbaikan atau penambahan terkait keamanan |

---

[Unreleased]: https://github.com/Athallah1234/All-In-One-Video-Downloader/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Athallah1234/All-In-One-Video-Downloader/releases/tag/v1.0.0
