import unittest
import tempfile
import datetime
import os
import shutil

from ...models import mediafile

class MediaFileInitTests(unittest.TestCase):
    def setUp(self):
        #  Create a temporary sandbox dir
        self.sandbox = tempfile.mkdtemp()

        #  Create a 'source' mirror
        self.source = os.path.join(self.sandbox, 'source')
        os.mkdir(self.source)

        #  Create a 'videos' library in the 'source' mirror
        self.source_videos = os.path.join(self.source, 'videos')
        os.mkdir(self.source_videos)

        #  Create a 'backup' mirror
        self.backup = os.path.join(self.sandbox, 'backup')
        os.mkdir(self.backup)

        #  Create a 'videos' library in the 'backup' mirror
        self.backup_videos = os.path.join(self.backup, 'videos')
        os.mkdir(self.backup_videos)

    def tearDown(self):
        shutil.rmtree(self.sandbox)

    def test_init_source_media(self):
        #  Make a mock video
        video = os.path.join(self.source_videos, 'mock.mkv')
        with open(video, 'w') as video_file:
            video_file.write('some bits')
        
        #  Make a MediaFile object
        media_file = mediafile.MediaFile(video, 'videos/mock.mkv', True)
        self.assertEqual(media_file.path, video)
        self.assertEqual(media_file.path_in_library, 'videos/mock.mkv')
        self.assertEqual(media_file.ext, '.mkv')
        self.assertTrue(media_file.source)
        fully_qualified_cache_file_path = os.path.join(self.source_videos, '.cache/mock.mkv.txt')
        self.assertEqual(media_file.cache_file, fully_qualified_cache_file_path)

    def test_init_backup_media(self):
        #  Make a mock video
        video = os.path.join(self.backup_videos, 'mock.mkv')
        with open(video, 'w') as video_file:
            video_file.write('some bits')
        
        #  Make a MediaFile object
        media_file = mediafile.MediaFile(video, 'videos/mock.mkv', False)
        self.assertEqual(media_file.path, video)
        self.assertEqual(media_file.path_in_library, 'videos/mock.mkv')
        self.assertEqual(media_file.ext, '.mkv')
        self.assertFalse(media_file.source)
        fully_qualified_cache_file_path = os.path.join(self.backup_videos, '.cache/mock.mkv.txt')
        self.assertEqual(media_file.cache_file, fully_qualified_cache_file_path)

    def test_real_checksum(self):
        #  Make a mock video
        video = os.path.join(self.backup_videos, 'mock1.mkv')
        with open(video, 'w') as video_file:
            video_file.write('some bits')

        #  Make a MediaFile object
        media_file = mediafile.MediaFile(video, 'videos/mock1.mkv', True)

        #  Assert the checksum is as expected
        self.assertEqual(media_file.real_hash, '523deb7dda45c48a991494b320d866a51a753f02')

        #  Make another mock video with different bits
        another_video = os.path.join(self.backup_videos, 'mock2.mkv')
        with open(another_video, 'w') as video_file:
            video_file.write('some more bits')

        #  Make another MediaFile object
        another_media_file = mediafile.MediaFile(another_video, 'videos/mock2.mkv', True)

        #  Assert the checksum is as expected
        self.assertEqual(another_media_file.real_hash, '65da63b7ee0b35ea8b37b195fea3e30ca9409eec')

    def test_cached_checksum(self):
        #  Make a mock video
        video = os.path.join(self.backup_videos, 'mock1.mkv')
        with open(video, 'w') as video_file:
            video_file.write('some bits')

        #  Make a MediaFile object
        media_file = mediafile.MediaFile(video, 'videos/mock1.mkv', True)

        #  Assert the cached checksum is as expected
        self.assertEqual(media_file.cached_hash, '523deb7dda45c48a991494b320d866a51a753f02')

        #  Make another mock video with different bits
        another_video = os.path.join(self.backup_videos, 'mock2.mkv')
        with open(another_video, 'w') as video_file:
            video_file.write('some more bits')

        #  Make another MediaFile object
        another_media_file = mediafile.MediaFile(another_video, 'videos/mock2.mkv', True)

        #  Assert the checksum is as expected
        self.assertEqual(another_media_file.cached_hash, '65da63b7ee0b35ea8b37b195fea3e30ca9409eec')

    def test_cached_checksum_date(self):
        #  Make a mock video
        video = os.path.join(self.backup_videos, 'mock.mkv')
        with open(video, 'w') as video_file:
            video_file.write('some bits')

        #  Make a MediaFile object
        media_file = mediafile.MediaFile(video, 'videos/mock.mkv', True)

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