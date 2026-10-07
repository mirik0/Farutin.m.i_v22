from .shell import Shell


def main():
    Shell().repl()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
