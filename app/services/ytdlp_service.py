from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from threading import Event
from urllib.parse import urlparse


class CancelledError(Exception): pass


def _non_negative_int(value):
    return value if isinstance(value,int) and not isinstance(value,bool) and value>=0 else None


def _upload_date(value):
    return value if isinstance(value,str) and len(value)==8 and value.isascii() and value.isdigit() else None


UNAVAILABLE_TITLE="[Video tidak tersedia]"


def _playlist_item(entry,position):
    source=entry if isinstance(entry,dict) else {}; explicit_index=source.get("playlist_index")
    index=explicit_index if isinstance(explicit_index,int) and not isinstance(explicit_index,bool) and explicit_index>0 else position
    title=source.get("title")
    return {"index":index,"title":title if isinstance(title,str) and title.strip() else UNAVAILABLE_TITLE,"id":source.get("id") if isinstance(source.get("id"),str) else "","availability":source.get("availability") if isinstance(source.get("availability"),str) else ""}


def _playlist_items(entries):
    if entries is None or isinstance(entries,(str,bytes,dict)):return ()
    return tuple(_playlist_item(entry,position) for position,entry in enumerate(entries,1))


def _valid_playlist_selector(value):
    if not isinstance(value,str) or not value:return False
    for part in value.split(","):
        pieces=part.split("-")
        if len(pieces) not in {1,2} or any(not piece.isascii() or not piece.isdigit() or int(piece)<=0 for piece in pieces):return False
        if len(pieces)==2 and int(pieces[0])>int(pieces[1]):return False
    return True


@dataclass
class DownloadRequest:
    url: str
    output_dir: Path
    download_mode: str = "Video + Audio"
    format_mode: str = "Best video + best audio"
    quality: str = "Best"
    custom_format: str = ""
    subtitles: bool = False
    auto_subtitles: bool = False
    subtitle_languages: str = "all"
    embed_subtitles: bool = False
    embed_thumbnail: bool = False
    embed_metadata: bool = False
    write_info_json: bool = False
    write_description: bool = False
    write_thumbnail: bool = False
    download_all_items: bool = True
    playlist_selection_mode: str = "all"
    playlist_items: str = ""
    playlist_start: int | None = None
    playlist_end: int | None = None
    open_after_download: bool = False
    skip_unavailable: bool = False
    preserve_structure: bool = False
    cookies_file: str = ""
    cookies_browser: str = ""
    proxy: str = ""
    filename_template: str = "%(title)s [%(id)s].%(ext)s"
    ffmpeg_path: str = ""


class YtDlpService:
    @staticmethod
    def installed_version():
        try:value=metadata.version("yt-dlp")
        except Exception:return None
        if not isinstance(value,str) or not value.strip():return None
        return value.strip()

    @staticmethod
    def validate_url(url: str) -> bool:
        parsed = urlparse(url.strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    @staticmethod
    def classify_info(info: dict) -> str:
        kind, extractor = info.get("_type", ""), info.get("extractor", "").lower()
        if "channel" in extractor: return "channel"
        if kind in {"playlist", "multi_video"}: return "playlist"
        if extractor == "generic": return "generic"
        return "video"

    @classmethod
    def normalize_info(cls, info: dict) -> dict:
        playlist_items = _playlist_items(info.get("entries"))
        explicit_count = _non_negative_int(info.get("playlist_count"))
        count = explicit_count if explicit_count is not None else (len(playlist_items) if playlist_items else None)
        description = info.get("description")
        return {"title": info.get("title") or "Tanpa judul", "uploader": info.get("uploader") or info.get("channel") or "-", "duration": info.get("duration"), "thumbnail": info.get("thumbnail") or "", "extractor": info.get("extractor_key") or info.get("extractor") or "Unknown", "type": cls.classify_info(info), "count":count, "playlist_items":playlist_items, "webpage_url": info.get("webpage_url") or info.get("original_url") or "", "description": description if isinstance(description,str) else "", "view_count":_non_negative_int(info.get("view_count")), "like_count":_non_negative_int(info.get("like_count")), "upload_date":_upload_date(info.get("upload_date"))}

    def build_options(self, request: DownloadRequest, progress=None, logger=None) -> dict:
        if not self.validate_url(request.url):
            raise ValueError("URL tidak valid.")
        if request.playlist_selection_mode not in {"all","range","selected"}:raise ValueError("Mode pilihan playlist tidak valid.")
        effective_scope=request.playlist_selection_mode
        if effective_scope=="all" and (request.playlist_start or request.playlist_end):effective_scope="range"
        if effective_scope=="selected":
            if request.playlist_start or request.playlist_end:raise ValueError("Pilihan playlist konflik dengan range.")
            if not _valid_playlist_selector(request.playlist_items):raise ValueError("Format pilihan playlist tidak valid.")
        elif request.playlist_items:raise ValueError("Pilihan playlist konflik dengan mode download.")
        if request.playlist_start and request.playlist_end and request.playlist_start > request.playlist_end:
            raise ValueError("Nilai awal range tidak boleh lebih besar dari nilai akhir.")
        if request.cookies_file and not Path(request.cookies_file).expanduser().is_file():
            raise ValueError("File cookies tidak ditemukan.")
        if request.proxy and urlparse(request.proxy).scheme not in {"http", "https", "socks4", "socks5", "socks5h"}:
            raise ValueError("Proxy harus berupa URL lengkap, misalnya http://127.0.0.1:8080.")
        heights = {"8K":4320,"4K":2160,"1440p":1440,"1080p":1080,"720p":720,"480p":480,"360p":360}
        mode = request.download_mode if request.download_mode in {"Video + Audio", "Video Only", "Audio Only"} else "Video + Audio"
        limit = f"[height<={heights[request.quality]}]" if request.quality in heights else ""
        if request.custom_format.strip(): selector = request.custom_format.strip()
        elif mode == "Audio Only": selector = "bestaudio/best"
        elif mode == "Video Only": selector = f"bestvideo{limit}/bestvideo"
        else: selector = f"bestvideo{limit}+bestaudio/best{limit}/best"
        out = Path(request.output_dir)
        template = request.filename_template
        if request.preserve_structure:
            template = "%(channel|uploader|playlist_title|Unknown)s/%(playlist_title|channel|uploader|Downloads)s/%(playlist_index|autonumber)03d - " + template
        opts = {"format":selector, "outtmpl":str(out / template), "noplaylist":False if effective_scope in {"range","selected"} else not request.download_all_items, "ignoreerrors":request.skip_unavailable, "continuedl":True, "retries":10, "fragment_retries":10, "file_access_retries":5, "extractor_retries":5, "windowsfilenames":__import__("os").name=="nt", "quiet":True}
        if progress: opts["progress_hooks"] = [progress]
        if logger: opts["logger"] = logger
        if effective_scope=="range" and request.playlist_start: opts["playliststart"] = request.playlist_start
        if effective_scope=="range" and request.playlist_end: opts["playlistend"] = request.playlist_end
        if effective_scope=="selected":opts["playlist_items"]=request.playlist_items
        if request.subtitles or request.embed_subtitles: opts["writesubtitles"] = True
        if request.auto_subtitles: opts["writeautomaticsub"] = True
        if request.subtitles or request.auto_subtitles or request.embed_subtitles: opts["subtitleslangs"] = [x.strip() for x in request.subtitle_languages.split(",") if x.strip()] or ["all"]
        audio_formats = {"MP3", "M4A", "AAC", "FLAC", "WAV", "OPUS", "OGG"}
        can_embed_subtitles = mode != "Audio Only" and request.format_mode not in audio_formats
        opts.update({
            "embedsubtitles": request.embed_subtitles and can_embed_subtitles,
            "writethumbnail": request.write_thumbnail or request.embed_thumbnail,
            "embedthumbnail": request.embed_thumbnail,
            "embedmetadata": request.embed_metadata,
            "writeinfojson": request.write_info_json,
            "writedescription": request.write_description,
            "keepvideo": False,
        })
        # WebP/AVIF artwork is rejected by several common media containers.
        # JPEG gives yt-dlp/FFmpeg a consistently embeddable thumbnail input.
        if request.embed_thumbnail:
            opts["convertthumbnails"] = "jpg"
        if request.cookies_file: opts["cookiefile"] = request.cookies_file
        if request.cookies_browser: opts["cookiesfrombrowser"] = (request.cookies_browser,)
        if request.proxy: opts["proxy"] = request.proxy
        if request.ffmpeg_path: opts["ffmpeg_location"] = request.ffmpeg_path
        postprocessors = []
        if mode == "Audio Only" and request.format_mode in audio_formats:
            bitrate = request.quality[:-1] if request.quality.endswith("k") and request.format_mode not in {"FLAC", "WAV"} else "0"
            postprocessors.append({"key":"FFmpegExtractAudio","preferredcodec":request.format_mode.lower(),"preferredquality":bitrate})
        elif mode in {"Video + Audio", "Video Only"}:
            if request.format_mode in {"MP4", "WEBM", "MKV"}:
                opts["merge_output_format"] = request.format_mode.lower()
            elif request.format_mode == "MOV":
                postprocessors.append({"key":"FFmpegVideoRemuxer","preferedformat":"mov"})
        if request.embed_thumbnail:
            postprocessors.append({"key":"FFmpegThumbnailsConvertor", "format":"jpg", "when":"before_dl"})
        if request.embed_metadata:
            postprocessors.append({"key":"FFmpegMetadata", "add_chapters":True, "add_metadata":True, "add_infojson":False})
        if request.embed_thumbnail:
            postprocessors.append({"key":"EmbedThumbnail", "already_have_thumbnail":request.write_thumbnail})
        if postprocessors:
            opts["postprocessors"] = postprocessors
        return opts

    def analyze(self, url: str) -> dict:
        if not self.validate_url(url): raise ValueError("URL tidak valid. Gunakan alamat HTTP atau HTTPS lengkap.")
        import yt_dlp
        with yt_dlp.YoutubeDL({"quiet":True,"skip_download":True,"extract_flat":"in_playlist"}) as ydl:
            return self.normalize_info(ydl.extract_info(url, download=False))

    def download(self, request: DownloadRequest, progress=None, logger=None, cancel_event: Event | None = None):
        import yt_dlp
        def hook(data):
            if cancel_event and cancel_event.is_set(): raise CancelledError("Download dibatalkan")
            if progress: progress(data)
        with yt_dlp.YoutubeDL(self.build_options(request, hook, logger)) as ydl: return ydl.extract_info(request.url, download=True)

    @staticmethod
    def list_extractors() -> list[str]:
        import yt_dlp.extractor
        return sorted({x.IE_NAME for x in yt_dlp.extractor.gen_extractor_classes() if getattr(x, "IE_NAME", None)}, key=str.lower)

    @staticmethod
    def friendly_error(error: Exception) -> str:
        text = str(error); low = text.lower()
        if isinstance(error, CancelledError): return "Download dibatalkan."
        if "ffmpeg" in low: return "FFmpeg tidak ditemukan atau tidak dapat dijalankan."
        if "private" in low or "login" in low: return "Konten bersifat privat atau memerlukan login/cookies."
        if "age" in low: return "Konten dibatasi usia; gunakan cookies akun yang memiliki akses."
        if "unsupported" in low: return "URL belum didukung atau situs telah berubah. Coba perbarui yt-dlp."
        if "permission" in low: return "Izin ditolak. Pilih folder keluaran lain."
        if "network" in low or "timed out" in low or "connection" in low: return "Masalah jaringan saat menghubungi situs."
        return text or "Terjadi kesalahan yang tidak diketahui."
