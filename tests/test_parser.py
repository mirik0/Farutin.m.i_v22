
import unittest

from src.parser import parse_command


class ParserTests(unittest.TestCase):

    def test_quoted_path(self):
        self.assertEqual(parse_command('cd "my folder"'),
                         ["cd", "my folder"])
        self.assertEqual(parse_command("ls 'my folder'"),
                         ["ls", "my folder"])

    def test_empty_and_comment(self):
        self.assertEqual(parse_command("   "), [])
        self.assertEqual(parse_command("# пример"), [])
        self.assertEqual(parse_command('ls "a#b" # текст'), ["ls", "a#b"])

    def test_unclosed_quote(self):
        with self.assertRaises(ValueError):
            parse_command('cd "folder')
