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

    def test_delete_media_from_source_video_library(self):
        LibraryTestMethods().delete_media(self.sandbox.source_videos_library)
    
    def test_delete_media_from_backup_video_library(self):
        LibraryTestMethods().delete_media(self.sandbox.backup_videos_library)

    def test_ignore_txt_in_source_video_library(self):
        file_path = self.sandbox.make_media(
            'ignore_me.txt',
            'foo',
            self.sandbox.source_videos_library
        )
        LibraryTestMethods().ignored_file_extensions(
            self.sandbox.source_videos_library,
            file_path
        )

    def test_ignore_txt_in_backup_video_library(self):
        file_path = self.sandbox.make_media(
            'ignore_me.txt',
            'foo',
            self.sandbox.backup_videos_library
        )
        LibraryTestMethods().ignored_file_extensions(
            self.sandbox.backup_videos_library,
            file_path
        )

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
                target_file_last_modified = os.path.getmtime(target_library_object.media[media_name].path)
                with self.assertRaises(FileExistsError):
                    target_library_object.copy_media(
                        other_library_object.media[media_name].path,
                        other_library_object.media[media_name].path_in_library,
                        other_library_object.media[media_name].real_hash
                    )
                self.assertTrue(media_name in target_library_object.media)
                self.assertTrue(os.path.exists(target_library_object.media[media_name].path))
                self.assertEqual(
                    target_file_last_modified,
                    os.path.getmtime(target_library_object.media[media_name].path)
                )

        self.assertEqual(len(target_library_object.media), original_target_media_count)

    def delete_media(self, mock_library):
        #  Make a Library object
        library_object = library.Library(mock_library.name, mock_library.path, mock_library.source)

        #  Load the library; assert media were actually found
        library_object.load_all_media()
        self.assertEqual(len(library_object.media), 18)

        #  Generate a cache file for each media in the library
        media_items = []
        for media_name in library_object.media:
            media_items.append((
                media_name,
                library_object.media[media_name].path
            ))
            library_object.media[media_name].cached_hash
            self.assertTrue(os.path.exists(library_object.media[media_name].cache_file))

        #  Delete each media and perform assertions
        for media_name, media_path in media_items:
            media_cache_path = library_object.media[media_name].cache_file
            library_object.delete_media(media_name)
            self.assertFalse(os.path.exists(media_path))
            self.assertFalse(os.path.exists(media_cache_path))
            self.assertFalse(media_name in library_object.media)

        self.assertEqual(len(library_object.media), 0)

    def ignored_file_extensions(self, mock_library, file_to_ignore):
        #  Make a Library object
        library_object = library.Library(mock_library.name, mock_library.path, mock_library.source)

        #  For sanity purposes, make sure the 'file_to_ignore' actually exists under the library
        self.assertTrue(os.path.exists(file_to_ignore.path))
        self.assertIn(library_object.path, file_to_ignore.path)

        #  Load the library; assert the 'file_to_ignore' was not loaded
        library_object.load_all_media()
        self.assertEqual(len(library_object.media), 18)
        self.assertNotIn(
            file_to_ignore.name,
            library_object.media
        )
