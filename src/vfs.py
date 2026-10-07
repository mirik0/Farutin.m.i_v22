
import base64
import json
import posixpath
from pathlib import Path


class VFS:

    def __init__(self, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.name = data["name"]
        self.dirs = set(data["directories"])
        self.files = {}
        for name, content in data["files"].items():
            if "text" in content:
                self.files[name] = content["text"].encode("utf-8")
            else:
                self.files[name] = base64.b64decode(
                    content["base64"], validate=True)
        self.validate()

    def validate(self):
        if "/" not in self.dirs:
            raise ValueError("VFS: отсутствует корневой каталог /")
        if self.dirs.intersection(self.files):
            raise ValueError("VFS: путь занят и файлом, и каталогом")
        for path in list(self.dirs) + list(self.files):
            normalized = posixpath.normpath(path)
            if not path.startswith("/") or path != normalized:
                raise ValueError(f"VFS: неверный абсолютный путь {path}")
            if path.startswith("//"):
                raise ValueError(f"VFS: неверный абсолютный путь {path}")
            if posixpath.dirname(path) not in self.dirs:
                raise ValueError(f"VFS: нет родителя для {path}")

    def show_motd(self):
        if "/motd" in self.files:
            text = self.files["/motd"].decode("utf-8", errors="replace")
            print(text, end="" if text.endswith("\n") else "\n")
