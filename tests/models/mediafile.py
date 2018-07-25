import unittest
import tempfile
import datetime
import os
import shutil

from ...models import mediafile

class MediaFileTests(unittest.TestCase):
    def setUp(self):
        #  Create a temporary sandbox dir
        self.sandbox = tempfile.mkdtemp()

        #  Create a 'source' mirror
        self.source = os.path.join(self.sandbox, 'source')
        os.mkdir(self.source)

        #  Create a 'videos' library in the 'source' mirror
        self.source_video_library = os.path.join(self.source, 'videos')
        os.mkdir(self.source_video_library)

        #  Create a mock video put it in the source 'videos' library
        self.source_video_file = os.path.join(self.source_video_library, 'mock.mkv')
        with open(self.source_video_file, 'w') as video_file:
            video_file.write('source bits')

        #  Create a 'backup' mirror
        self.backup = os.path.join(self.sandbox, 'backup')
        os.mkdir(self.backup)

        #  Create a 'videos' library in the 'backup' mirror
        self.backup_video_library = os.path.join(self.backup, 'videos')
        os.mkdir(self.backup_video_library)

        #  Create a mock video put it in the backup 'videos' library
        self.backup_video_file = os.path.join(self.backup_video_library, 'mock.mkv')
        with open(self.backup_video_file, 'w') as video_file:
            video_file.write('backup bits')

    def tearDown(self):
        shutil.rmtree(self.sandbox)

    def test_init_source_media(self):
        #  Make a MediaFile object
        media_file = mediafile.MediaFile(self.source_video_file, 'videos/mock.mkv', True)

        #  Assert default properties are as expected
        self.assertEqual(media_file.path, self.source_video_file)
        self.assertEqual(media_file.path_in_library, 'videos/mock.mkv')
        self.assertEqual(media_file.ext, '.mkv')
        self.assertTrue(media_file.source)
        fully_qualified_cache_file_path = os.path.join(self.source_video_library, '.cache/mock.mkv.txt')
        self.assertEqual(media_file.cache_file, fully_qualified_cache_file_path)

    def test_init_backup_media(self):
        #  Make a MediaFile object
        media_file = mediafile.MediaFile(self.backup_video_file, 'videos/mock.mkv', False)

        #  Assert default properties are as expected
        self.assertEqual(media_file.path, self.backup_video_file)
        self.assertEqual(media_file.path_in_library, 'videos/mock.mkv')
        self.assertEqual(media_file.ext, '.mkv')
        self.assertFalse(media_file.source)
        fully_qualified_cache_file_path = os.path.join(self.backup_video_library, '.cache/mock.mkv.txt')
        self.assertEqual(media_file.cache_file, fully_qualified_cache_file_path)

    def test_real_checksum(self):
        #  Make a 'source' MediaFile object
        source_media_file = mediafile.MediaFile(self.source_video_file, 'videos/mock.mkv', True)

        #  Assert the checksum is as expected
        self.assertEqual(source_media_file.real_hash, '1a571c4ef14eb5de03dcc5dfb6faa716c74759eb')

        #  Make a 'backup' MediaFile object
        backup_media_file = mediafile.MediaFile(self.backup_video_file, 'videos/mock.mkv', True)

        #  Assert the checksum is as expected
        self.assertEqual(backup_media_file.real_hash, '3614f5ce63f53e30693d6e0e7be976d2d932f274')

    def test_cached_checksum(self):
        #  Make a 'source' MediaFile object
        source_media_file = mediafile.MediaFile(self.source_video_file, 'videos/mock.mkv', True)

        #  Assert the cached checksum is as expected
        self.assertEqual(source_media_file.cached_hash, '1a571c4ef14eb5de03dcc5dfb6faa716c74759eb')

        #  Make a 'backup' MediaFile object
        backup_media_file = mediafile.MediaFile(self.backup_video_file, 'videos/mock.mkv', True)

        #  Assert the checksum is as expected
        self.assertEqual(backup_media_file.cached_hash, '3614f5ce63f53e30693d6e0e7be976d2d932f274')

    def test_cached_checksum_date(self):
        #  Make a MediaFile object
        media_file = mediafile.MediaFile(self.source_video_file, 'videos/mock.mkv', True)

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
