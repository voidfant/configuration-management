import unittest
from unittest.mock import patch, mock_open, MagicMock
import io
import tarfile
from datetime import datetime

from src.vfs import VirtualFileSystem
from src.common.file import File

class TestVirtualFileSystem(unittest.TestCase):
    def setUp(self):
        self.fs = VirtualFileSystem()
        self.fs.files = {
            "/": File("/", b"", True, datetime.now().timestamp()),
            "/home": File("/home", b"", True, datetime.now().timestamp()),
            "/home/user": File("/home/user", b"", True, datetime.now().timestamp()),
            "/home/user/file.txt": File("/home/user/file.txt", b"content", False, datetime.now().timestamp()),
            "/home/user/doc.pdf": File("/home/user/doc.pdf", b"pdf content", False, datetime.now().timestamp())
        }
        self.fs.current_directory = "/"

    def test_ls_root(self):
        """Test 1: ls in root directory"""
        self.assertEqual(self.fs.ls("/"), ["home"])

    def test_ls_empty_dir(self):
        """Test 2: ls in empty directory"""
        self.fs.files["/empty"] = File("/empty", b"", True, datetime.now().timestamp())
        self.assertEqual(self.fs.ls("/empty"), [])

    def test_ls_with_files(self):
        """Test 3: ls in directory with files"""
        self.assertEqual(
            self.fs.ls("/home/user"),
            ["doc.pdf", "file.txt"]
        )

    def test_cd_valid(self):
        """Test 1: cd to valid directory"""
        self.assertTrue(self.fs.cd("/home"))
        self.assertEqual(self.fs.current_directory, "/home")

    def test_cd_invalid(self):
        """Test 2: cd to non-existent directory"""
        self.assertFalse(self.fs.cd("/nonexistent"))
        self.assertEqual(self.fs.current_directory, "/")

    def test_cd_file(self):
        """Test 3: cd to file (should fail)"""
        self.assertFalse(self.fs.cd("/home/user/file.txt"))
        self.assertEqual(self.fs.current_directory, "/")

    def test_rm_file(self):
        """Test 1: rm single file"""
        self.assertTrue(self.fs.rm("/home/user/file.txt"))
        self.assertNotIn("/home/user/file.txt", self.fs.files)

    def test_rm_directory(self):
        """Test 2: rm directory and its contents"""
        self.assertTrue(self.fs.rm("/home/user"))
        self.assertNotIn("/home/user", self.fs.files)
        self.assertNotIn("/home/user/file.txt", self.fs.files)
        self.assertNotIn("/home/user/doc.pdf", self.fs.files)

    def test_rm_nonexistent(self):
        """Test 3: rm non-existent file"""
        self.assertFalse(self.fs.rm("/nonexistent"))

    def test_find_exact(self):
        """Test 1: find exact filename"""
        results = self.fs.find("/home", "file.txt")
        self.assertEqual(results, ["/home/user/file.txt"])

    def test_find_pattern(self):
        """Test 2: find using pattern"""
        results = self.fs.find("/home", ".*\.pdf")
        self.assertEqual(results, ["/home/user/doc.pdf"])

    def test_find_no_match(self):
        """Test 3: find with no matches"""
        results = self.fs.find("/home", "nonexistent")
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()