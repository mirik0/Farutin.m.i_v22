
import shlex

MAX_PATHS = 1


def parse_command(line):
    return shlex.split(line, comments=True, posix=True)


def parse_options(args, allowed):
    flags = set()
    paths = []
    options = True
    for arg in args:
        if options and arg == "--":
            options = False
        elif options and arg.startswith("-") and arg != "-":
            for flag in arg[1:]:
                if flag not in allowed:
                    raise ValueError(f"неизвестный флаг: -{flag}")
                flags.add(flag)
        else:
            paths.append(arg)
    return flags, paths


def single_path(args, default):
    if len(args) > MAX_PATHS:
        raise ValueError("нужен не более одного пути")
    return args[0] if args else default


def no_args(args, command):
    if args:
        raise ValueError(f"{command}: аргументы не нужны")
