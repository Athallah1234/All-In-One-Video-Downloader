from app.ui.about_dialog import build_about_html


def test_about_html_contains_dynamic_versions():
    text=build_about_html("1.2.3","2026.07.01","3.12.4","6.9.0")
    assert "Modern Video Downloader 1.2.3" in text
    assert "yt-dlp:</b> 2026.07.01" in text
    assert "Python:</b> 3.12.4" in text
    assert "PySide6:</b> 6.9.0" in text


def test_about_html_escapes_all_dynamic_values():
    text=build_about_html("<app>","<yt>","<python>","<qt>")
    assert "<app>" not in text and "&lt;app&gt;" in text
    assert "<yt>" not in text and "&lt;yt&gt;" in text
    assert "<python>" not in text and "&lt;python&gt;" in text
    assert "<qt>" not in text and "&lt;qt&gt;" in text


def test_about_html_uses_fallback_for_missing_versions():
    text=build_about_html("1.0.0",None,None,None)
    assert text.count("Tidak tersedia")==3
