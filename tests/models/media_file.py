import unittest
import datetime
import os

from ..tools import sandbox
from ...models import media_file

class MediaFileTests(unittest.TestCase):
    #  Run before/after every unit test

    def setUp(self):
        #  Create a sandbox in a temporary (safe) directory
        self.sandbox = sandbox.Sandbox()
        self.sandbox.create()

        #  Create mock video file(s) in the source 'Videos' library
        self.source_mock_file = self.sandbox.make_media('mock.mkv', 'source bits', self.sandbox.source_videos_library)
        self.source_mock_file_in_dir = self.sandbox.make_media('dir/mock.mkv', 'source bits', self.sandbox.source_videos_library)

        #  Create mock video file(s) in the backup 'Videos' library
        self.backup_mock_file = self.sandbox.make_media('mock.mkv', 'backup bits', self.sandbox.backup_videos_library)
        self.backup_mock_file_in_dir = self.sandbox.make_media('dir/mock.mkv', 'backup bits', self.sandbox.backup_videos_library)

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
    
    def init_media_file(self, mock_file: sandbox.MockMediaFile):
        #  Make a MediaFile object
        media_file_object = media_file.MediaFile(
            mock_file.path,
            mock_file.name,
            mock_file.source
        )

        #  Assert default properties are as expected
        self.assertEqual(media_file_object.path, mock_file.path)
        self.assertEqual(media_file_object.path_in_library, mock_file.name)
        self.assertEqual(media_file_object.ext, '.mkv')
        self.assertEqual(media_file_object.source, mock_file.source)

        mock_file_dirname = os.path.dirname(mock_file.path)
        mock_file_cache_file = os.path.join(
            mock_file_dirname,
            '.cache',
            '{}.txt'.format(os.path.basename(mock_file.name))
        )

        self.assertEqual(media_file_object.cache_file, mock_file_cache_file)

    def real_checksum(self, mock_file: sandbox.MockMediaFile, checksum: str):
        #  Make a 'backup' MediaFile object
        backup_media_file_object = media_file.MediaFile(mock_file.path, mock_file.name, mock_file.source)

        #  Assert the checksum is as expected
        self.assertEqual(backup_media_file_object.real_checksum, checksum)

    def cached_checksum(self, mock_file: sandbox.MockMediaFile, checksum: str):
        #  Make a MediaFile object
        media_file_object = media_file.MediaFile(mock_file.path, mock_file.name, mock_file.source)

        #  Assert the checksum is as expected
        self.assertEqual(media_file_object.cached_checksum, checksum)

    def cached_checksum_date(self, mock_file: sandbox.MockMediaFile):
        #  Make a MediaFile object
        media_file_object = media_file.MediaFile(mock_file.path, mock_file.name, mock_file.source)

        #  Assert the generated cache date is today
        today = str(datetime.date.today())
        self.assertEqual(media_file_object.cached_date, today)

        #  Assert the cache is not flagged as 'stale'
        self.assertFalse(media_file_object.cache_is_stale(stale_cache_days=90))

        #  Modify the cache date for the next assertion
        with open(media_file_object.cache_file, 'r') as cache_file:
            cached_checksum = cache_file.readline().split('|')[1]
        with open(media_file_object.cache_file, 'w') as cache_file:
            cache_file.write('{}|{}'.format('2018-04-01', cached_checksum))

        #  Assert the modified cache date is returned
        media_file_object.load_cache_file()
        self.assertEqual(media_file_object.cached_date, '2018-04-01')

        #  Assert the cache is flagged as 'stale'
        self.assertTrue(media_file_object.cache_is_stale(stale_cache_days=90))