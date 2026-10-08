
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src.shell import Shell
from src.vfs import VFS


class RemoveTests(unittest.TestCase):

    def setUp(self):
        self.vfs = VFS("fixtures/multiple.json")
        self.shell = Shell(self.vfs)

    def execute(self, line):
        with redirect_stdout(io.StringIO()):
            return self.shell.execute(line)

    def test_files_and_source(self):
        source = Path("fixtures/multiple.json")
        before = source.read_bytes()
        self.assertTrue(self.execute("rm readme.txt binary.bin"))
        self.assertNotIn("/readme.txt", self.vfs.files)
        self.assertNotIn("/binary.bin", self.vfs.files)
        self.assertEqual(source.read_bytes(), before)
        self.assertIn("/readme.txt", VFS(source).files)

    def test_recursive(self):
        for option in ("-r", "-R", "-rf", "-fr"):
            with self.subTest(option=option):
                self.setUp()
                self.assertTrue(self.execute(f"rm {option} docs"))
                self.assertNotIn("/docs", self.vfs.dirs)
                self.assertNotIn("/docs/note.txt", self.vfs.files)

    def test_missing_and_force(self):
        self.assertFalse(self.execute("rm missing"))
        self.assertFalse(self.execute("rm"))
        self.assertTrue(self.execute("rm -f missing"))
        self.assertTrue(self.execute("rm -rf missing/child"))
        self.assertTrue(self.execute("rm -f"))
        self.assertFalse(self.execute("rm -f docs"))

    def test_directory_without_flag(self):
        self.assertFalse(self.execute("rm empty"))
        self.assertTrue(self.execute("rm -r empty"))

    def test_quoted_relative_path(self):
        self.execute('cd "my folder"')
        self.assertTrue(self.execute("rm 'file name.txt'"))
        self.assertNotIn("/my folder/file name.txt", self.vfs.files)

    def test_root_and_current_directory(self):
        self.assertFalse(self.execute("rm -rf /"))
        self.execute("cd docs")
        self.assertFalse(self.execute("rm -r ."))
        self.assertFalse(self.execute("rm -r .."))
        self.assertIn("/docs/note.txt", self.vfs.files)

    def test_unknown_flag_and_separator(self):
        self.assertFalse(self.execute("rm -z readme.txt"))
        self.vfs.files["/-file"] = b"data"
        self.assertTrue(self.execute("rm -- -file"))
        self.assertNotIn("/-file", self.vfs.files)

    def test_prefix_boundary(self):
        self.vfs.dirs.add("/docs2")
        self.vfs.files["/docs2/keep.txt"] = b"keep"
        self.assertTrue(self.execute("rm -r /docs"))
        self.assertIn("/docs2/keep.txt", self.vfs.files)

    def test_deep_tree(self):
        self.vfs = VFS("fixtures/deep.json")
        self.shell = Shell(self.vfs)
        self.assertTrue(self.execute("rm -r /level1"))
        self.assertEqual(self.vfs.dirs, {"/"})
        self.assertEqual(set(self.vfs.files), {"/motd"})
