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

        #  Load the library again; the same number of media should be in the library
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
        #  Make 'source' and 'backup' Library objects
        source_library_object = library.Library('videos', True, self.source_video_library)
        backup_library_object = library.Library('videos', False, self.backup_video_library)

        #  Delete all backup media
        for media_file in self.backup_video_list:
            os.remove(media_file)
        self.backup_video_list = []

        #  Load the 'source' and 'backup' libraries
        #  The 'backup' library should be empty
        source_library_object.load_all_media()
        backup_library_object.load_all_media()
        self.assertEqual(len(source_library_object.media), len(self.source_video_list))
        self.assertEqual(len(backup_library_object.media), 0)

        #  Copy all media from 'source' to 'backup'
        #  Assert each copy action creates a new MediaFile object in the 'backup' library
        for media_name, source_media_file_object in source_library_object.media.items():
            backup_library_object.copy_media(
                source_media_file_object.path,
                media_name,
                source_media_file_object.real_hash
            )
            self.assertTrue(media_name in backup_library_object.media)
            backup_media_file_object = backup_library_object.media[media_name]
            self.assertEqual(backup_media_file_object.real_hash, source_media_file_object.real_hash)
            self.assertEqual(backup_media_file_object.cached_hash, source_media_file_object.cached_hash)
            self.assertEqual(backup_media_file_object.cached_date, str(datetime.date.today()))
            self.assertFalse(backup_media_file_object.cache_is_stale)

        #  Delete all 'source' media
        for media_file in self.source_video_list:
            os.remove(media_file)
        self.source_video_list = []

        #  Empty the 'source' library's 'media' list
        #  Assert both libraries have the expected number of items in their 'media' lists
        source_library_object.media = {}
        self.assertEqual(len(source_library_object.media), 0)
        self.assertEqual(len(backup_library_object.media), 11)

        #  Copy all media from 'backup' to 'source'
        #  Assert each copy action creates a new MediaFile object in the 'source' library
        for media_name, backup_media_file_object in backup_library_object.media.items():
            source_library_object.copy_media(
                backup_media_file_object.path,
                media_name,
                backup_media_file_object.real_hash
            )
            self.assertTrue(media_name in source_library_object.media)
            source_media_file_object = source_library_object.media[media_name]
            self.assertEqual(source_media_file_object.real_hash, backup_media_file_object.real_hash)
            self.assertEqual(source_media_file_object.cached_hash, backup_media_file_object.cached_hash)
            self.assertEqual(source_media_file_object.cached_date, str(datetime.date.today()))
            self.assertFalse(source_media_file_object.cache_is_stale)        

        #  Assert both libraries have the expected number of items in their 'media' lists
        self.assertEqual(len(source_library_object.media), 11)
        self.assertEqual(len(backup_library_object.media), 11)

    def test_delete_media(self):
        #  Make 'source' and 'backup' Library objects
        source_library_object = library.Library('videos', True, self.source_video_library)
        backup_library_object = library.Library('videos', False, self.backup_video_library)

        #  Load the 'source' and 'backup' libraries
        source_library_object.load_all_media()
        backup_library_object.load_all_media()

        #  Assert the libraries actually contain media files
        self.assertEqual(len(source_library_object.media), len(self.source_video_list))
        self.assertEqual(len(backup_library_object.media), len(self.source_video_list))

        #  Set a reference to the first media file in each library
        source_file_name = next(iter(source_library_object.media))
        backup_file_name = next(iter(backup_library_object.media))
        source_file = source_library_object.media[source_file_name]
        backup_file = backup_library_object.media[backup_file_name]

        #  Generate a cache file for one file in each library
        source_file.save_hash_to_file(False)
        backup_file.save_hash_to_file(False)

        #  Assert the cache files exist
        self.assertTrue(os.path.exists(source_file.cache_file))
        self.assertTrue(os.path.exists(backup_file.cache_file))

        #  Delete both media
        source_library_object.delete_media(source_file_name)
        backup_library_object.delete_media(backup_file_name)

        #  Assert both media and both cache files no longer exist on the disc
        self.assertFalse(os.path.exists(source_file.path))
        self.assertFalse(os.path.exists(backup_file.path))
        self.assertFalse(os.path.exists(source_file.cache_file))
        self.assertFalse(os.path.exists(backup_file.cache_file))

        #  Assert neither media exist in their libraries any more
        self.assertFalse(source_file_name in source_library_object.media.keys())
        self.assertFalse(backup_file_name in backup_library_object.media.keys())
        self.assertEqual(len(source_library_object.media), 10)
        self.assertEqual(len(backup_library_object.media), 10)
        
    def test_directory_media(self):
        #  Implementation notes
        #    The reason for asserting 'delete_media()' works here as well
        #    is to help determine where the defect exists, if a unit test fails.
        #
        #    If 'test_directory_media()' fails when deleting, but 'test_delete_media()' passes
        #    it is obvious the defect only exists when deleting /directory/ media.
        #
        #    This is the same logic for having a 'test_load_all_media()' test plus another
        #    'test_directory_media()' test, that basically does the same thing
        #    but with media in directories

        #  Make and load a 'source' library object
        source_library_object = library.Library('videos', True, self.source_video_library)
        source_library_object.load_all_media()

        #  Assert the number of media in the library is as expected
        self.assertEqual(len(source_library_object.media), len(self.source_video_list))

        #  Add a new file to the disc; the file is in a sub-directory
        file_directory = os.path.join(self.source_video_library, 'sub-dir')
        file_path = os.path.join(file_directory, 'directory-test.mkv')
        media_file_name = 'sub-dir/directory-test.mkv'
        os.mkdir(file_directory)
        self.source_video_list.append(file_path)
        with open(file_path, 'w') as video_file:
            video_file.write('source bits')

        #  Load the library again
        source_library_object.load_all_media()

        #  Assert the new media is added to the library
        self.assertTrue(media_file_name in source_library_object.media.keys())
        self.assertEqual(source_library_object.media[media_file_name].path_in_library, media_file_name)
        self.assertEqual(source_library_object.media[media_file_name].path, file_path)
        self.assertEqual(len(source_library_object.media), len(self.source_video_list))

        #  Create the cache file for the media, then call 'delete_media()'
        directory_media_file = source_library_object.media[media_file_name]
        directory_media_file.save_hash_to_file(False)
        source_library_object.delete_media(media_file_name)
        self.source_video_list.remove(file_path)

        #  Assert the media was deleted as expected
        self.assertFalse(os.path.exists(directory_media_file.path))
        self.assertFalse(os.path.exists(directory_media_file.cache_file))
        self.assertFalse(media_file_name in source_library_object.media.keys())
        self.assertEqual(len(source_library_object.media), len(self.source_video_list))

        #  todo - test 'copy_media()'

    def test_ignored_file_extensions(self):
        #  Make a 'source' library object
        source_library_object = library.Library('videos', True, self.source_video_library)
        
        #  Add a file to the disc that is not in the library's list of allowed extensions
        file_path = os.path.join(self.source_video_library, 'bad-extension.txt')
        with open(file_path, 'w') as new_file:
            new_file.write('source bits')

        #  Load the library and assert the new file is not loaded
        source_library_object.load_all_media()
        self.assertFalse('bad-extension.txt' in source_library_object.media.keys())
        self.assertEqual(len(source_library_object.media), len(self.source_video_list))

    def test_yield_empty_directories(self):
        #  todo
        self.assertTrue(False)

    def test_delete_empty_directories(self):
        #  todo
        self.assertTrue(False)

    def test_yield_orphan_cache_files(self):
        #  todo
        self.assertTrue(False)

    def test_delete_orphan_cache_files(self):
        #  todo
        self.assertTrue(False)