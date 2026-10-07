
import time
from datetime import datetime, timedelta
from pathlib import Path

from .parser import no_args, parse_command, parse_options, single_path


class Shell:

    def __init__(self, vfs, config=None):
        self.vfs = vfs
        self.name = vfs.name
        self.cwd = "/"
        self.running = True
        self.config = config or {"vfs": "", "script": ""}
        self.started = time.monotonic()
        self.commands = {
            "ls": self.ls,
            "cd": self.cd,
            "date": self.date,
            "uptime": self.uptime,
            "pwd": self.pwd,
            "exit": self.exit,
            "conf-dump": self.conf_dump,
        }

    def prompt(self):
        return f"{self.name}:{self.cwd}$ "

    def execute(self, line):
        try:
            words = parse_command(line)
            if not words:
                return True
            command, *args = words
            if command not in self.commands:
                raise ValueError(f"неизвестная команда: {command}")
            self.commands[command](args)
            return True
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")
            return False

    def ls(self, args):
        flags, paths = parse_options(args, "a")
        path = self.vfs.resolve(single_path(paths, self.cwd), self.cwd)
        for name in self.vfs.list_names(path, "a" in flags):
            print(name)

    def cd(self, args):
        path = self.vfs.resolve(single_path(args, "/"), self.cwd)
        if path not in self.vfs.dirs:
            raise NotADirectoryError(f"не каталог: {path}")
        self.cwd = path

    def pwd(self, args):
        no_args(args, "pwd")
        print(self.cwd)

    def date(self, args):
        no_args(args, "date")
        print(datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"))

    def uptime(self, args):
        no_args(args, "uptime")
        seconds = int(time.monotonic() - self.started)
        print(f"up {timedelta(seconds=seconds)}")

    def exit(self, args):
        no_args(args, "exit")
        self.running = False

    def conf_dump(self, args):
        no_args(args, "conf-dump")
        for key, value in self.config.items():
            print(f"{key}={value}")

    def run_script(self, path):
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, start=1):
            if not self.running:
                break
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            print(self.prompt() + line)
            if not self.execute(line):
                print(f"Скрипт остановлен: строка {number}")
                return False
        return True

    def repl(self):
        while self.running:
            try:
                line = input(self.prompt())
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print()
                continue
            self.execute(line)
