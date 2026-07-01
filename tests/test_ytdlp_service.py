import pytest

from app.services.ytdlp_service import DownloadRequest, YtDlpService


def test_installed_version_returns_clean_distribution_version(monkeypatch):
    monkeypatch.setattr("app.services.ytdlp_service.metadata.version",lambda name:" 2026.07.01 ")
    assert YtDlpService.installed_version()=="2026.07.01"


@pytest.mark.parametrize("result",["","   ",None,123])
def test_installed_version_rejects_malformed_values(monkeypatch,result):
    monkeypatch.setattr("app.services.ytdlp_service.metadata.version",lambda name:result)
    assert YtDlpService.installed_version() is None


def test_installed_version_contains_metadata_failures(monkeypatch):
    def fail(name):raise RuntimeError("metadata rusak")
    monkeypatch.setattr("app.services.ytdlp_service.metadata.version",fail)
    assert YtDlpService.installed_version() is None


@pytest.mark.parametrize("raw,expected", [
    ("Baris satu\nBaris dua 🚀", "Baris satu\nBaris dua 🚀"),
    (None, ""),
    (123, ""),
])
def test_normalize_info_safely_preserves_description(raw, expected):
    assert YtDlpService.normalize_info({"description": raw})["description"] == expected


@pytest.mark.parametrize("raw,expected", [(0,0),(123456789,123456789),(None,None),(True,None),(-1,None),(1.5,None),("100",None)])
def test_normalize_info_validates_counts(raw, expected):
    result = YtDlpService.normalize_info({"view_count":raw, "like_count":raw})
    assert result["view_count"] == expected
    assert result["like_count"] == expected


@pytest.mark.parametrize("raw,expected", [("20251231","20251231"),(None,None),(20251231,None),("2025-12-31",None),("abcdefgh",None),("202512311",None)])
def test_normalize_info_validates_upload_date_shape(raw, expected):
    assert YtDlpService.normalize_info({"upload_date":raw})["upload_date"] == expected


def test_normalize_info_preserves_playlist_positions_and_fields():
    info={"_type":"playlist","entries":[{"title":"Satu","id":"a","availability":"public"},None,{"title":"","playlist_index":9},"rusak",{"title":"<b>Unicode 🚀</b>","playlist_index":True}]}
    result=YtDlpService.normalize_info(info)
    assert result["playlist_items"] == (
        {"index":1,"title":"Satu","id":"a","availability":"public"},
        {"index":2,"title":"[Video tidak tersedia]","id":"","availability":""},
        {"index":9,"title":"[Video tidak tersedia]","id":"","availability":""},
        {"index":4,"title":"[Video tidak tersedia]","id":"","availability":""},
        {"index":5,"title":"<b>Unicode 🚀</b>","id":"","availability":""},
    )
    assert result["count"] == 5


def test_normalize_info_materializes_generator_once():
    entries=({"title":f"Video {index}"} for index in range(3))
    result=YtDlpService.normalize_info({"_type":"playlist","entries":entries})
    assert [item["title"] for item in result["playlist_items"]] == ["Video 0","Video 1","Video 2"]
    assert result["count"] == 3


def test_normalize_info_prefers_valid_explicit_playlist_count():
    result=YtDlpService.normalize_info({"_type":"playlist","playlist_count":10,"entries":[{"title":"Satu"}]})
    assert result["count"] == 10


def test_validate_and_classify():
    assert YtDlpService.validate_url("https://example.com/watch?v=1")
    assert not YtDlpService.validate_url("not a url")
    assert YtDlpService.classify_info({"_type": "playlist", "extractor": "youtube:tab"}) == "playlist"
    assert YtDlpService.classify_info({"extractor": "generic"}) == "generic"


@pytest.mark.parametrize("mode,expected", [("Audio Only", "bestaudio/best"), ("Video Only", "bestvideo"), ("Video + Audio", "bestvideo")])
def test_format_mapping(mode, expected, tmp_path):
    options = YtDlpService().build_options(DownloadRequest(url="https://example.com/a", output_dir=tmp_path, download_mode=mode))
    assert expected in options["format"]


def test_build_options_for_combined_video_audio(tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, download_mode="Video + Audio", format_mode="MP4", quality="1080p")
    options = YtDlpService().build_options(request)
    assert options["format"] == "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"
    assert options["merge_output_format"] == "mp4"


def test_build_options_for_video_only(tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, download_mode="Video Only", format_mode="WEBM", quality="720p")
    options = YtDlpService().build_options(request)
    assert options["format"] == "bestvideo[height<=720]/bestvideo"
    assert options["merge_output_format"] == "webm"


def test_build_options_for_audio_bitrate(tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, download_mode="Audio Only", format_mode="MP3", quality="192k")
    options = YtDlpService().build_options(request)
    assert options["format"] == "bestaudio/best"
    assert options["postprocessors"] == [{"key":"FFmpegExtractAudio", "preferredcodec":"mp3", "preferredquality":"192"}]


def test_build_options_for_best_m4a(tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, download_mode="Audio Only", format_mode="M4A", quality="Best")
    options = YtDlpService().build_options(request)
    assert options["postprocessors"] == [{"key":"FFmpegExtractAudio", "preferredcodec":"m4a", "preferredquality":"0"}]


@pytest.mark.parametrize("container", ["MP4", "WEBM", "MKV"])
def test_video_merge_containers(container, tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, format_mode=container)
    assert YtDlpService().build_options(request)["merge_output_format"] == container.lower()


def test_mov_uses_ffmpeg_remux(tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, format_mode="MOV")
    options = YtDlpService().build_options(request)
    assert options["postprocessors"] == [{"key":"FFmpegVideoRemuxer", "preferedformat":"mov"}]
    assert "merge_output_format" not in options


@pytest.mark.parametrize("codec", ["MP3", "M4A", "AAC", "OPUS", "OGG"])
def test_lossy_audio_codecs_use_selected_bitrate(codec, tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, download_mode="Audio Only", format_mode=codec, quality="256k")
    postprocessor = YtDlpService().build_options(request)["postprocessors"][0]
    assert postprocessor == {"key":"FFmpegExtractAudio", "preferredcodec":codec.lower(), "preferredquality":"256"}


@pytest.mark.parametrize("codec", ["FLAC", "WAV"])
def test_lossless_audio_codecs_use_best(codec, tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, download_mode="Audio Only", format_mode=codec, quality="Best")
    postprocessor = YtDlpService().build_options(request)["postprocessors"][0]
    assert postprocessor == {"key":"FFmpegExtractAudio", "preferredcodec":codec.lower(), "preferredquality":"0"}


def test_custom_selector_keeps_selected_container(tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, custom_format="137+140/22", format_mode="MKV")
    options = YtDlpService().build_options(request)
    assert options["format"] == "137+140/22"
    assert options["merge_output_format"] == "mkv"


def test_playlist_and_subtitle_options(tmp_path):
    req = DownloadRequest(url="https://example.com/list", output_dir=tmp_path, playlist_start=2, playlist_end=4, subtitles=True, subtitle_languages="id,en", skip_unavailable=True)
    options = YtDlpService().build_options(req)
    assert options["playliststart"] == 2
    assert options["playlistend"] == 4
    assert options["subtitleslangs"] == ["id", "en"]
    assert options["ignoreerrors"] is True


def test_selected_playlist_items_map_to_ytdlp(tmp_path):
    request=DownloadRequest("https://example.com/list",tmp_path,playlist_selection_mode="selected",playlist_items="1-3,5,8-9")
    options=YtDlpService().build_options(request)
    assert options["noplaylist"] is False
    assert options["playlist_items"]=="1-3,5,8-9"
    assert "playliststart" not in options and "playlistend" not in options


@pytest.mark.parametrize("selector",["","1,,2","1-","0","3-1","a","1 2"])
def test_selected_playlist_items_reject_invalid_selectors(selector,tmp_path):
    with pytest.raises(ValueError,match="pilihan playlist"):
        YtDlpService().build_options(DownloadRequest("https://example.com/list",tmp_path,playlist_selection_mode="selected",playlist_items=selector))


def test_range_mode_rejects_selected_items(tmp_path):
    request=DownloadRequest("https://example.com/list",tmp_path,playlist_selection_mode="range",playlist_start=2,playlist_end=4,playlist_items="1")
    with pytest.raises(ValueError,match="konflik"):
        YtDlpService().build_options(request)


def test_all_items_and_single_item_are_distinct(tmp_path):
    all_options = YtDlpService().build_options(DownloadRequest("https://example.com/list", tmp_path))
    single_options = YtDlpService().build_options(DownloadRequest("https://example.com/list", tmp_path, download_all_items=False))
    assert all_options["noplaylist"] is False
    assert single_options["noplaylist"] is True


def test_custom_format_takes_precedence(tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, format_mode="Custom", custom_format="137+140/22")
    assert YtDlpService().build_options(request)["format"] == "137+140/22"


def test_embed_subtitles_enables_subtitle_download_and_conversion(tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, embed_subtitles=True, subtitle_languages="id, en")
    options = YtDlpService().build_options(request)
    assert options["writesubtitles"] is True
    assert options["subtitleslangs"] == ["id", "en"]
    assert options["embedsubtitles"] is True


def test_video_only_does_not_fallback_to_muxed_format(tmp_path):
    request = DownloadRequest("https://example.com/v", tmp_path, download_mode="Video Only", quality="720p")
    assert YtDlpService().build_options(request)["format"] == "bestvideo[height<=720]/bestvideo"


def test_request_validation_rejects_invalid_range_and_inputs(tmp_path):
    service = YtDlpService()
    with pytest.raises(ValueError, match="range"):
        service.build_options(DownloadRequest("https://example.com/list", tmp_path, playlist_start=5, playlist_end=2))
    with pytest.raises(ValueError, match="cookies"):
        service.build_options(DownloadRequest("https://example.com/v", tmp_path, cookies_file=str(tmp_path / "missing.txt")))
    with pytest.raises(ValueError, match="Proxy"):
        service.build_options(DownloadRequest("https://example.com/v", tmp_path, proxy="localhost:8080"))


def test_structure_template_has_safe_channel_and_playlist_fallbacks(tmp_path):
    request = DownloadRequest("https://example.com/list", tmp_path, preserve_structure=True)
    template = YtDlpService().build_options(request)["outtmpl"]
    assert "%(channel|uploader|playlist_title|Unknown)s" in template
    assert "%(playlist_title|channel|uploader|Downloads)s" in template


@pytest.mark.parametrize("format_mode,quality", [
    ("MP4", "Best"), ("MP4", "1080p"), ("WEBM", "720p"),
    ("MKV", "4K"), ("MOV", "480p"),
    ("MP3", "320k"), ("M4A", "Best"), ("AAC", "192k"),
    ("FLAC", "Best"), ("WAV", "Best"), ("OPUS", "128k"), ("OGG", "256k"),
])
def test_embed_options_survive_every_format_and_quality(format_mode, quality, tmp_path):
    mode = "Audio Only" if format_mode in {"MP3", "M4A", "AAC", "FLAC", "WAV", "OPUS", "OGG"} else "Video + Audio"
    request = DownloadRequest(
        "https://example.com/v", tmp_path, download_mode=mode,
        format_mode=format_mode, quality=quality, embed_thumbnail=True,
        embed_metadata=True, embed_subtitles=True,
    )
    options = YtDlpService().build_options(request)
    assert options["writethumbnail"] is True
    assert options["embedthumbnail"] is True
    assert options["convertthumbnails"] == "jpg"
    assert options["embedmetadata"] is True
    assert options["writesubtitles"] is True
    assert options["embedsubtitles"] is (mode != "Audio Only")
    assert options["keepvideo"] is False


def test_embed_options_create_real_ytdlp_postprocessors(tmp_path):
    import yt_dlp

    request = DownloadRequest(
        "https://example.com/v", tmp_path, download_mode="Audio Only",
        format_mode="MP3", embed_thumbnail=True, embed_metadata=True,
    )
    ydl = yt_dlp.YoutubeDL(YtDlpService().build_options(request))
    names = [type(pp).__name__ for pps in ydl._pps.values() for pp in pps]
    assert names == [
        "FFmpegThumbnailsConvertorPP",
        "FFmpegExtractAudioPP",
        "FFmpegMetadataPP",
        "EmbedThumbnailPP",
    ]
