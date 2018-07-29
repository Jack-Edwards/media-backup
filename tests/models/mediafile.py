import unittest
import tempfile
import datetime
import os
import shutil

from ..tools import sandbox
from ...models import mediafile

class MediaFileTests(unittest.TestCase):
    #  Run before/after every unit test

    def setUp(self):
        #  Create a sandbox in a temporary (safe) directory
        self.sandbox = sandbox.Sandbox()
        self.sandbox.create()

        #  Create mock video file(s) in the source 'Videos' library
        self.source_mock_file = self.sandbox.make_media('mock.mkv', 'source bits', 'Videos', True)
        self.source_mock_file_in_dir = self.sandbox.make_media('dir/mock.mkv', 'source bits', 'Videos', True)

        #  Create mock video file(s) in the backup 'Videos' library
        self.backup_mock_file = self.sandbox.make_media('mock.mkv', 'backup bits', 'Videos', False)
        self.backup_mock_file_in_dir = self.sandbox.make_media('dir/mock.mkv', 'backup bits', 'Videos', False)

    def tearDown(self):
        self.sandbox.destroy()

    #  Unit tests

    def test_init_source_media(self):
        MediaFileTestMethods().init_media_file(self.source_mock_file)

    def test_init_source_media_in_directory(self):
        MediaFileTestMethods().init_media_file(self.source_mock_file_in_dir)

    def test_init_backup_media(self):
        MediaFileTestMethods().init_media_file(self.backup_mock_file)

    def test_init_backup_media_in_directory(self):
        MediaFileTestMethods().init_media_file(self.backup_mock_file_in_dir)

    def test_source_real_checksum(self):
        MediaFileTestMethods().real_checksum(
            self.source_mock_file,
            '1a571c4ef14eb5de03dcc5dfb6faa716c74759eb',
        )

    def test_source_real_checksum_in_directory(self):
        MediaFileTestMethods().real_checksum(
            self.source_mock_file_in_dir,
            '1a571c4ef14eb5de03dcc5dfb6faa716c74759eb',
        )

    def test_backup_real_checksum(self):
        MediaFileTestMethods().real_checksum(
            self.backup_mock_file,
            '3614f5ce63f53e30693d6e0e7be976d2d932f274',
        )

    def test_backup_real_checksum_in_directory(self):
        MediaFileTestMethods().real_checksum(
            self.backup_mock_file_in_dir,
            '3614f5ce63f53e30693d6e0e7be976d2d932f274',
        )

    def test_source_cached_checksum(self):
        MediaFileTestMethods().cached_checksum(
            self.source_mock_file,
            '1a571c4ef14eb5de03dcc5dfb6faa716c74759eb'
        )

    def test_source_cached_checksum_in_directory(self):
        MediaFileTestMethods().cached_checksum(
            self.source_mock_file_in_dir,
            '1a571c4ef14eb5de03dcc5dfb6faa716c74759eb'
        )

    def test_backup_cached_checksum(self):
        MediaFileTestMethods().cached_checksum(
            self.backup_mock_file,
            '3614f5ce63f53e30693d6e0e7be976d2d932f274'
        )

    def test_backup_cached_checksum_in_directory(self):
        MediaFileTestMethods().cached_checksum(
            self.backup_mock_file_in_dir,
            '3614f5ce63f53e30693d6e0e7be976d2d932f274'
        )

    def test_source_cached_checksum_date(self):
        MediaFileTestMethods().cached_checksum_date(self.source_mock_file)

    def test_backup_cached_checksum_date(self):
        MediaFileTestMethods().cached_checksum_date(self.backup_mock_file)

class MediaFileTestMethods(unittest.TestCase):
    #  Re-usable methods
    
    def init_media_file(self, mock_file):
        #  Make a MediaFile object
        media_file = mediafile.MediaFile(
            mock_file.path,
            mock_file.name,
            False
        )

        #  Assert default properties are as expected
        self.assertEqual(media_file.path, mock_file.path)
        self.assertEqual(media_file.path_in_library, mock_file.name)
        self.assertEqual(media_file.ext, '.mkv')
        self.assertFalse(media_file.source)

        mock_file_dirname = os.path.dirname(mock_file.path)
        mock_file_cache_file = os.path.join(
            mock_file_dirname,
            '.cache',
            '{}.txt'.format(os.path.basename(mock_file.name))
        )

        self.assertEqual(media_file.cache_file, mock_file_cache_file)

    def real_checksum(self, mock_file, checksum):
        #  Make a 'backup' MediaFile object
        backup_media_file = mediafile.MediaFile(mock_file.path, mock_file.name, False)

        #  Assert the checksum is as expected
        self.assertEqual(backup_media_file.real_hash, checksum)

    def cached_checksum(self, mock_file, checksum):
        #  Make a MediaFile object
        media_file = mediafile.MediaFile(mock_file.path, mock_file.name, False)

        #  Assert the checksum is as expected
        self.assertEqual(media_file.cached_hash, checksum)

    def cached_checksum_date(self, mock_file):
        #  Make a MediaFile object
        media_file = mediafile.MediaFile(mock_file.path, mock_file.name, True)

        #  Assert the generated cache date is today
        today = str(datetime.date.today())
        self.assertEqual(media_file.cached_date, today)

        #  Assert the cache is not flagged as 'stale'
        self.assertFalse(media_file.cache_is_stale)

        #  Modify the cache date for the next assertion
        with open(media_file.cache_file, 'r') as cache_file:
            cached_checksum = cache_file.readline().split('|')[1]
        with open(media_file.cache_file, 'w') as cache_file:
            cache_file.write('{}|{}'.format('2018-04-01', cached_checksum))

        #  Assert the modified cache date is returned
        media_file.load_hash_from_file()
        self.assertEqual(media_file.cached_date, '2018-04-01')

        #  Assert the cache is flagged as 'stale'
        self.assertTrue(media_file.cache_is_stale)