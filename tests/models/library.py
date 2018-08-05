import unittest
import datetime
import os

from ..tools import sandbox
from ...models import library

class LibraryTests(unittest.TestCase):
    def setUp(self):
        #  Create a sandbox in a temporary (safe) directory
        self.sandbox = sandbox.Sandbox()
        self.sandbox.create()

        #  Add unique files to each 'Videos' library
        self.unique_source_files = self.sandbox.populate_library_with_unique_media(self.sandbox.source_videos_library)
        self.unique_backup_files = self.sandbox.populate_library_with_unique_media(self.sandbox.backup_videos_library)
        
        #  Add matching files to both 'Videos' library
        self.matching_source_files, self.matching_backup_files = self.sandbox.populate_libraries_with_identical_media(
            self.sandbox.source_videos_library,
            self.sandbox.backup_videos_library
        )

    def tearDown(self):
        self.sandbox.destroy()

    def test_init_source_videos_library(self):
        LibraryTestMethods().init_library(self.sandbox.source_videos_library)

    def test_init_source_music_library(self):
        LibraryTestMethods().init_library(self.sandbox.source_music_library)

    def test_init_backup_videos_library(self):
        LibraryTestMethods().init_library(self.sandbox.backup_videos_library)

    def test_init_backup_music_library(self):
        LibraryTestMethods().init_library(self.sandbox.backup_music_library)

    def test_load_all_from_source_videos_library(self):
        media_in_library = self.unique_source_files + self.matching_source_files
        LibraryTestMethods().load_all_media(self.sandbox.source_videos_library, media_in_library)

    def test_load_all_from_backup_videos_library(self):
        media_in_library = self.unique_backup_files + self.matching_backup_files
        LibraryTestMethods().load_all_media(self.sandbox.backup_videos_library, media_in_library)

    def test_copy_new_media_to_source_video_library(self):
        LibraryTestMethods().copy_new_media(
            self.sandbox.source_videos_library,
            self.sandbox.backup_videos_library
        )

    def test_copy_new_media_to_backup_source_video_library(self):
        LibraryTestMethods().copy_new_media(
            self.sandbox.backup_videos_library,
            self.sandbox.source_videos_library
        )

    def test_copy_existing_media_to_source_video_library(self):
        LibraryTestMethods().copy_existing_media(
            self.sandbox.source_videos_library,
            self.sandbox.backup_videos_library
        )

    def test_copy_existing_media_to_backup_video_library(self):
        LibraryTestMethods().copy_existing_media(
            self.sandbox.backup_videos_library,
            self.sandbox.source_videos_library
        )

    def test_delete_media(self):
        return
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
        return
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
        return
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

class LibraryTestMethods(unittest.TestCase):
    #  Re-usable methods

    def init_library(self, mock_library: sandbox.MockLibrary):
        #  Make a Library object
        library_object = library.Library(mock_library.name, mock_library.path, mock_library.source)

        #  Assert default properties are as expected
        self.assertEqual(library_object.name, mock_library.name)
        self.assertEqual(library_object.path, mock_library.path)
        self.assertEqual(library_object.source, mock_library.source)
        self.assertEqual(len(library_object.media), 0)

    def load_all_media(self, mock_library: sandbox.MockLibrary, media_in_library: list):
        #  Make a Library object
        library_object = library.Library(mock_library.name, mock_library.path, mock_library.source)

        #  Load all media and assert all media were found
        library_object.load_all_media()
        self.assertEqual(len(media_in_library), len(library_object.media))

        #  Load all media again; assert the library's list of media did not change
        library_object.load_all_media()
        self.assertEqual(len(media_in_library), len(library_object.media))

        #  Assert all files were init'd properly
        for media_name in library_object.media:
            #  Assert the MediaFile 'path' is the absolute path to the file
            self.assertTrue(library_object.media[media_name].path in [item.path for item in media_in_library])

            #  Assert the MediaFile 'path_in_library' is the relative path to the file (relative to the library)
            #  Note: this is the same code used in the current Library().load_all_media() method
            path_in_library = library_object.media[media_name].path.replace(
                library_object.path + os.sep, ''
            )
            self.assertEqual(library_object.media[media_name].path_in_library, path_in_library)

            #  Assert the MediaFile 'source' is equal to the Library 'source'
            self.assertEqual(library_object.media[media_name].source, library_object.source)

            #  Remove the video from video_list for the next 'for' iteration
            #  to prove the same media is not returned more than once
            media_in_library.remove(list(filter(lambda x: x.name == media_name, media_in_library))[0])

    def copy_new_media(self, target_mock_library: sandbox.MockLibrary, other_mock_library: sandbox.MockLibrary):
        #  Make a pair of Library objects
        target_library_object = library.Library(target_mock_library.name, target_mock_library.path, target_mock_library.source)
        other_library_object = library.Library(other_mock_library.name, other_mock_library.path, other_mock_library.source)

        #  Load the Library objects
        target_library_object.load_all_media()
        other_library_object.load_all_media()

        original_target_media_count = len(target_library_object.media)

        #  Copy media to 'target' that only exist in 'other'
        #  Assert each Library.copy_media() action creates a new MediaFile object in the 'target' library
        copy_count = 0
        for media_name in other_library_object.media:
            if media_name not in target_library_object.media:
                copy_count += 1
                target_library_object.copy_media(
                    other_library_object.media[media_name].path,
                    other_library_object.media[media_name].path_in_library,
                    other_library_object.media[media_name].real_hash
                )

                #  Assertions
                self.assertTrue(media_name in target_library_object.media)
                self.assertEqual(
                    target_library_object.media[media_name].path_in_library,
                    other_library_object.media[media_name].path_in_library
                )
                self.assertTrue(os.path.exists(target_library_object.media[media_name].path))
                self.assertEqual(
                    target_library_object.media[media_name].real_hash,
                    other_library_object.media[media_name].real_hash
                )
                self.assertNotEqual(
                    target_library_object.media[media_name].cache_file,
                    other_library_object.media[media_name].cache_file
                )
                self.assertEqual(
                    target_library_object.media[media_name].cached_hash,
                    other_library_object.media[media_name].cached_hash
                )
                self.assertEqual(
                    target_library_object.media[media_name].cached_date,
                    str(datetime.date.today())
                )
        #  Verify the above 'for' loop actually copied something
        #  Sandbox.populate_library_with_unique_media() adds 12 files
        self.assertEqual(copy_count, 12)  #  If this fails, the whole test was a dud
        self.assertEqual(len(target_library_object.media), original_target_media_count + copy_count)

    def copy_existing_media(self, target_mock_library: sandbox.MockLibrary, other_mock_library: sandbox.MockLibrary):
        #  Make a pair of Library objects
        target_library_object = library.Library(target_mock_library.name, target_mock_library.path, target_mock_library.source)
        other_library_object = library.Library(other_mock_library.name, other_mock_library.path, other_mock_library.source)

        #  Load the Library objects
        target_library_object.load_all_media()
        other_library_object.load_all_media()

        original_target_media_count = len(target_library_object.media)

        #  Attempt to copy media from 'other' that already exists on the 'target'
        #  Assert the file is /not/ copied
        copy_count = 0
        for media_name in other_library_object.media:
            if media_name in target_library_object.media:
                copy_count += 1
                with self.assertRaises(FileExistsError):
                    target_library_object.copy_media(
                        other_library_object.media[media_name].path,
                        other_library_object.media[media_name].path_in_library,
                        other_library_object.media[media_name].real_hash
                    )
                self.assertTrue(media_name in target_library_object.media)
                self.assertTrue(os.path.exists(target_library_object.media[media_name].path))
                #  todo - verify the file's last write datetime doesn't change (?)
                
        self.assertEqual(len(target_library_object.media), original_target_media_count)
