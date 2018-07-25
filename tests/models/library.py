import unittest
import tempfile
import datetime
import os
import shutil

from ...models import library

class LibraryTests(unittest.TestCase):
    def setUp(self):
        #  Create a temporary sandbox dir
        self.sandbox = tempfile.mkdtemp()

        #  Create a 'source' mirror
        self.source = os.path.join(self.sandbox, 'source')
        os.mkdir(self.source)

        #  Create a 'videos' library in the 'source' mirror
        self.source_video_library = os.path.join(self.source, 'videos')
        os.mkdir(self.source_video_library)

        #  Create a dozen mock videos put them in the source 'videos' library
        self.source_video_list = []
        for i in range(11):
            #  Name the video file
            file_name = 'mock-{}.mkv'.format(i+1)
            self.source_video_list.append(os.path.join(self.source_video_library, file_name))

            #  Make the video file
            with open(self.source_video_list[i], 'w') as video_file:
                video_file.write('source bits')

        #  Create a 'backup' mirror
        self.backup = os.path.join(self.sandbox, 'backup')
        os.mkdir(self.backup)

        #  Create a 'videos' library in the 'backup' mirror
        self.backup_video_library = os.path.join(self.backup, 'videos')
        os.mkdir(self.backup_video_library)

        #  Create a dozen mock videos put them in the backup 'videos' library
        self.backup_video_list = []
        for i in range(11):
            #  Name the video file
            file_name = 'mock-{}.mkv'.format(i+1)
            self.backup_video_list.append(os.path.join(self.backup_video_library, file_name))

            #  Make the video file
            with open(self.backup_video_list[i], 'w') as video_file:
                video_file.write('backup bits')

    def tearDown(self):
        shutil.rmtree(self.sandbox)

    def test_init_source_library(self):
        #  Make a Library object
        library_object = library.Library('videos', True, self.source_video_library)

        #  Assert default properties are as expected
        self.assertEqual(library_object.name, 'videos')
        self.assertTrue(library_object.source)
        self.assertEqual(library_object.path, self.source_video_library)
        self.assertEqual(len(library_object.media), 0)

    def test_init_backup_library(self):
        #  Make a Library object
        library_object = library.Library('videos', False, self.source_video_library)

        #  Assert default properties are as expected
        self.assertEqual(library_object.name, 'videos')
        self.assertFalse(library_object.source)
        self.assertEqual(library_object.path, self.source_video_library)
        self.assertEqual(0, len(library_object.media))

    def test_load_all_media(self):
        #  Make a 'source' Library object
        source_library_object = library.Library('videos', True, self.source_video_library)

        #  Assert all media are loaded
        source_library_object.load_all_media()
        self.assertEqual(len(self.source_video_list), len(source_library_object.media))

        #  Assert the media were loaded properly
        video_list = self.source_video_list
        for media_file in source_library_object.media:
            self.assertEqual(source_library_object.media[media_file].source, source_library_object.source)
            self.assertTrue(source_library_object.media[media_file].path in video_list)

            #  Build the path_in_library for the media file
            #  This is the same code used in the Library model
            filepath_in_library = source_library_object.media[media_file].path.replace(
                source_library_object.path + os.sep, ''
            )
            self.assertEqual(source_library_object.media[media_file].path_in_library, filepath_in_library)

            #  Remove the video from video_list for the next iteration
            #  To prove the same media is not returned more than once
            video_list.remove(source_library_object.media[media_file].path)

        #  Make a 'backup' Library object
        backup_library_object = library.Library('videos', False, self.backup_video_library)

        #  Assert all media are loaded
        backup_library_object.load_all_media()
        self.assertEqual(len(self.backup_video_list), len(backup_library_object.media))

        #  Assert the media were loaded properly
        video_list = self.backup_video_list
        for media_file in backup_library_object.media:
            self.assertEqual(backup_library_object.media[media_file].source, backup_library_object.source)
            self.assertTrue(backup_library_object.media[media_file].path in video_list)

            #  Build the path_in_library for the media file
            #  This is the same code used in the Library model
            filepath_in_library = backup_library_object.media[media_file].path.replace(
                backup_library_object.path + os.sep, ''
            )
            self.assertEqual(backup_library_object.media[media_file].path_in_library, filepath_in_library)

            #  Remove the video from video_list for the next iteration
            #  To prove the same media is not returned more than once
            video_list.remove(backup_library_object.media[media_file].path)

    def test_copy_media(self):
        #  todo
        self.assertTrue(False)

    def test_delete_media(self):
        #  todo
        self.assertTrue(False)

    def test_folder_media(self):
        #  todo
        self.assertTrue(False)

    def test_ignored_file_extensions(self):
        #  todo
        self.assertTrue(False)