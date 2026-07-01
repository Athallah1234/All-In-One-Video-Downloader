import shutil
from pathlib import Path


class FFmpegService:
    @staticmethod
    def resolve(configured: str = "") -> str | None:
        if configured:
            path = Path(configured).expanduser()
            if path.is_dir(): path = path / ("ffmpeg.exe" if __import__("os").name == "nt" else "ffmpeg")
            if path.is_file(): return str(path)
        return shutil.which("ffmpeg")
