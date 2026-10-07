
import shlex


def parse_command(line):
    return shlex.split(line, comments=True, posix=True)
