from .parser import parse_command


class Shell:
    def __init__(self, name="vfs"):
        self.name = name
        self.cwd = "/"
        self.running = True
        self.commands = {
            "ls": self.stub,
            "cd": self.stub,
            "exit": self.exit,
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
