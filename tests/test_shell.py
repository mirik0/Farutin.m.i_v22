
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from src.shell import Shell
from src.vfs import VFS


class ShellTests(unittest.TestCase):

    def setUp(self):
        self.shell = Shell(VFS("fixtures/multiple.json"))

    def run_command(self, line):
        output = io.StringIO()
        with redirect_stdout(output):
            success = self.shell.execute(line)
        return success, output.getvalue()

    def test_quoted_path(self):
        self.assertTrue(self.run_command('cd "my folder"')[0])
        self.assertEqual(self.shell.cwd, "/my folder")
        self.assertEqual(self.shell.prompt(), "study-vfs:/my folder$ ")

    def test_errors(self):
        for line in ("unknown", "cd a b", "exit extra", 'ls "bad'):
            with self.subTest(line=line):
                success, output = self.run_command(line)
                self.assertFalse(success)
                self.assertIn("Ошибка:", output)
                self.assertTrue(self.shell.running)

    def test_exit(self):
        self.assertTrue(self.run_command("exit")[0])
        self.assertFalse(self.shell.running)

    def test_interactive_recovery(self):
        with patch("builtins.input", side_effect=["unknown", "exit"]):
            with redirect_stdout(io.StringIO()):
                self.shell.repl()
        self.assertFalse(self.shell.running)

    def test_ls(self):
        success, output = self.run_command("ls")
        self.assertTrue(success)
        self.assertNotIn(".hidden", output)
        self.assertEqual(output.splitlines(), sorted(output.splitlines()))
        self.assertIn(".hidden", self.run_command("ls -a")[1])
        self.assertEqual(self.run_command("ls readme.txt")[1],
                         "readme.txt\n")
        self.assertEqual(self.run_command("ls empty")[1], "")

    def test_cd_and_pwd(self):
        self.assertTrue(self.run_command("cd docs")[0])
        self.assertEqual(self.run_command("pwd")[1], "/docs\n")
        self.assertTrue(self.run_command("cd .")[0])
        self.assertTrue(self.run_command("cd ..")[0])
        self.assertEqual(self.shell.cwd, "/")
        self.run_command("cd docs")
        self.run_command("cd")
        self.assertEqual(self.shell.cwd, "/")

    def test_path_errors(self):
        lines = ("cd readme.txt", "ls missing", "cd missing/..",
                 "ls readme.txt/..", "ls -z", "ls a b", 'cd ""')
        for line in lines:
            with self.subTest(line=line):
                self.assertFalse(self.run_command(line)[0])
                self.assertEqual(self.shell.cwd, "/")

    def test_simple_commands(self):
        with patch("src.shell.time.monotonic", return_value=100):
            self.shell.started = 35
            self.assertEqual(self.run_command("uptime")[1], "up 0:01:05\n")
        self.assertRegex(self.run_command("date")[1],
                         r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}")
        for command in ("pwd", "date", "uptime", "conf-dump"):
            self.assertFalse(self.run_command(command + " extra")[0])
