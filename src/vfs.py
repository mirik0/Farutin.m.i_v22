
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

    def resolve(self, path, cwd):
        if not path:
            raise ValueError("путь не может быть пустым")
        current = "/" if path.startswith("/") else cwd
        for part in path.split("/"):
            self.require_directory(current)
            if part in ("", "."):
                continue
            if part == "..":
                current = posixpath.dirname(current)
            else:
                current = posixpath.join(current, part)
                if current not in self.dirs and current not in self.files:
                    raise FileNotFoundError(f"путь не найден: {current}")
        if path.endswith("/"):
            self.require_directory(current)
        return current

    def require_directory(self, path):
        if path not in self.dirs:
            raise NotADirectoryError(f"не каталог: {path}")

    def list_names(self, path, show_all=False):
        if path in self.files:
            return [posixpath.basename(path)]
        names = []
        if show_all:
            names.extend([".", ".."])
        for item in list(self.dirs) + list(self.files):
            if item == "/" or posixpath.dirname(item) != path:
                continue
            name = posixpath.basename(item)
            if show_all or not name.startswith("."):
                names.append(name)
        return sorted(names)

    def remove(self, path, recursive, cwd):
        if path in self.files:
            del self.files[path]
            return
        if not recursive:
            raise IsADirectoryError(f"это каталог, нужен -r: {path}")
        if path == "/":
            raise ValueError("rm: нельзя удалять корень VFS")
        if cwd == path or cwd.startswith(path + "/"):
            raise ValueError("rm: нельзя удалять текущий каталог или родителя")
        self.remove_tree(path)

    def remove_tree(self, path):
        prefix = path + "/"
        for name in list(self.files):
            if name.startswith(prefix):
                del self.files[name]
        for name in list(self.dirs):
            if name == path or name.startswith(prefix):
                self.dirs.remove(name)
