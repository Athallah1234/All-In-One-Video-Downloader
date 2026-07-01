import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.config import DEFAULT_SETTINGS


class SettingsService:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> dict:
        values = DEFAULT_SETTINGS.copy()
        if not self.path.exists():
            return values
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            values.update({k: v for k, v in data.items() if k in values})
        except (OSError, ValueError, TypeError):
            try:
                self.path.replace(self.path.with_suffix(self.path.suffix + ".broken"))
            except OSError:
                pass
        return values

    def save(self, values: dict) -> dict:
        data = DEFAULT_SETTINGS.copy()
        data.update({k: v for k, v in values.items() if k in data})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=self.path.parent, suffix=".tmp") as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False)
            temp = Path(stream.name)
        temp.replace(self.path)
        return data

    def reset(self) -> dict:
        return self.save(DEFAULT_SETTINGS)
