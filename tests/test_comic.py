"""Test comic format."""
from pathlib import Path
from unittest import TestCase

from picopt.formats import comic

TEST_FILES_ROOT = 'tests/test_files'
COMIC_ROOT = TEST_FILES_ROOT+'/comic_archives'


class TestGetComicFormat(TestCase):

    def test_cbz(self) -> None:
        res = comic.get_comic_format(COMIC_ROOT+'/test_cbz.cbz')
        self.assertEqual(res, 'CBZ')

    def test_cbr(self) -> None:
        res = comic.get_comic_format(COMIC_ROOT+'/test_cbr.cbr')
        self.assertEqual(res, 'CBR')

    def test_dir(self) -> None:
        res = comic.get_comic_format(COMIC_ROOT)
        self.assertEqual(res, None)


class TestGetArchiveTmpDir(TestCase):

    def test_foo(self) -> None:
        res = comic._get_archive_tmp_dir(Path('foo'))
        self.assertEqual(str(res), 'picopt_tmp_foo')
