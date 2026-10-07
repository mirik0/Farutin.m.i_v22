
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.vfs import VFS


class VFSTests(unittest.TestCase):

    def test_fixtures(self):
        for name in ("minimal", "multiple", "deep"):
            with self.subTest(name=name):
                vfs = VFS(f"fixtures/{name}.json")
                self.assertIn("/", vfs.dirs)
        vfs = VFS("fixtures/multiple.json")
        self.assertEqual(vfs.files["/binary.bin"], bytes([0, 1, 2, 255]))

    def test_motd(self):
        output = io.StringIO()
        with redirect_stdout(output):
            VFS("fixtures/minimal.json").show_motd()
        self.assertEqual(output.getvalue(), "")
        with redirect_stdout(output):
            VFS("fixtures/multiple.json").show_motd()
        self.assertIn("Добро пожаловать", output.getvalue())

    def test_invalid_parent(self):
        data = {"name": "bad", "directories": ["/"],
                "files": {"/missing/a": {"text": "a"}}}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError):
                VFS(path)
