
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class MainTests(unittest.TestCase):

    def launch(self, args, stdin=""):
        return subprocess.run(
            [sys.executable, "-m", "src.main"] + args,
            input=stdin, text=True, capture_output=True,
        )

    def test_success(self):
        result = self.launch(["--vfs", "fixtures/multiple.json",
                              "--script", "scripts/startup/stage4.txt"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("vfs=fixtures/multiple.json", result.stdout)
        self.assertIn("Добро пожаловать", result.stdout)
        self.assertIn("study-vfs:/my folder$ pwd", result.stdout)

    def test_error_stops_script_and_repl(self):
        result = self.launch(["--script", "scripts/startup/stage5_error.txt"],
                             stdin="date\nexit\n")
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("$ pwd", result.stdout)
        self.assertNotIn("$ date", result.stdout)
        self.assertIn("Скрипт остановлен: строка 2", result.stdout)

    def test_startup_errors(self):
        for args in (["--vfs", "missing.json"],
                     ["--script", "missing.txt"], ["--unknown"]):
            with self.subTest(args=args):
                result = self.launch(args)
                self.assertNotEqual(result.returncode, 0)

    def test_script_then_repl(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "init.txt"
            path.write_text("cd docs\n", encoding="utf-8")
            result = self.launch(["--script", str(path)], "pwd\nexit\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("study-vfs:/docs$ /docs", result.stdout)
