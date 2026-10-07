
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from src.shell import Shell


class ShellTests(unittest.TestCase):

    def setUp(self):
        self.shell = Shell()

    def run_command(self, line):
        output = io.StringIO()
        with redirect_stdout(output):
            success = self.shell.execute(line)
        return success, output.getvalue()

    def test_stub(self):
        self.assertEqual(self.run_command('cd "my folder"'),
                         (True, "cd: ['my folder']\n"))

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
