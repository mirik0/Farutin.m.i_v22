
from .parser import parse_command
from pathlib import Path


class Shell:

    def __init__(self, name="vfs", config=None):
        self.name = name
        self.cwd = "/"
        self.running = True
        self.config = config or {"vfs": "", "script": ""}
        self.commands = {
            "ls": self.stub,
            "cd": self.stub,
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
            if command in ("ls", "cd"):
                self.stub([command] + args)
            else:
                self.commands[command](args)
            return True
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")
            return False

    def stub(self, args):
        command, *values = args
        if len(values) > 1:
            raise ValueError(f"{command}: нужен не более одного пути")
        print(f"{command}: {values}")

    def exit(self, args):
        if args:
            raise ValueError("exit: аргументы не нужны")
        self.running = False

    def conf_dump(self, args):
        if args:
            raise ValueError("conf-dump: аргументы не нужны")
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
