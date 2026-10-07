
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.shell import Shell
from src.vfs import VFS


class ScriptTests(unittest.TestCase):

    def run_script(self, text):
        shell = Shell(VFS("fixtures/multiple.json"))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "commands.txt"
            path.write_text(text, encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                success = shell.run_script(path)
        return shell, success, output.getvalue()

    def test_first_error(self):
        shell, success, output = self.run_script("unknown\nexit\n")
        self.assertFalse(success)
        self.assertTrue(shell.running)
        self.assertNotIn("$ exit", output)
        self.assertIn("строка 1", output)

    def test_exit_and_comments(self):
        shell, success, output = self.run_script("# текст\nexit\nbad\n")
        self.assertTrue(success)
        self.assertFalse(shell.running)
        self.assertNotIn("bad", output)

    def test_dump(self):
        shell = Shell(VFS("fixtures/multiple.json"),
                      config={"vfs": "a.json", "script": "b.txt"})
        output = io.StringIO()
        with redirect_stdout(output):
            shell.conf_dump([])
        self.assertEqual(output.getvalue(), "vfs=a.json\nscript=b.txt\n")
