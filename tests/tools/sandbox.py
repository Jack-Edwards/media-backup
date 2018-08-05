import hashlib
import os
import shutil
import tempfile


class MockMediaFile(object):
    def __init__(self, name: str, path: str, library_name: str, source: bool):
        self.name = name
        self.path = path
        self.library_name = library_name
        self.source = source

class MockLibrary(object):
    def __init__(self, name: str, path: str, source: str):
        self.name = name
        self.path = path
        self.source = source

class Sandbox(object):
    def __init__(self):
        self.path = None

    def create(self):
        #  Description
        #    Create a temporary directory for unit tests to run in
        #    Create mirror and library directories in the temporary directory
        #  Requires
        #    n/a
        #  Guarantees
        #    Temporary directory is created and set to 'self.path'
        #    Mirror and library directories are also set as object attributes

        if self.path:
            raise FileExistsError('Sandbox already exists')

        self.path = tempfile.mkdtemp()

        #  Add mirrors to the sandbox
        self.source_mirror = self.make_mirror(True)
        self.backup_mirror = self.make_mirror(False)

        #  Add libraries to the sandbox
        self.source_videos_library = self.make_library('Videos', True)
        self.source_music_library = self.make_library('Music', True)

        self.backup_videos_library = self.make_library('Videos', False)
        self.backup_music_library = self.make_library('Music', False)


    def destroy(self):
        #  Description
        #    Remove the sandbox directory, recursive
        #  Requires
        #    'self.path' must be a valid path
        #  Guarantees
        #    The path and all it's contents will be deleted
        #  Implementation Notes
        #    All object properties are left intact
        #    Do not continue testing with the sandbox after this method is called

        shutil.rmtree(self.path)

    def make_mirror(self, source: bool):
        #  Description
        #    Make a 'mirror' directory in the sandbox
        #    Return a path to the directory
        #  Requires
        #    'self.path' must exist on the disc
        #  Guarantees
        #    The 'mirror' directory is created and returned

        source_string = 'source' if source else 'backup'
        mirror_path = os.path.join(self.path, source_string)

        if os.path.exists(mirror_path):
            raise FileExistsError('Mirror already exists in sandbox')

        os.mkdir(mirror_path)
        return mirror_path

    def get_mirror_path(self, source: bool):
        #  Description
        #    Get the path to the matching mirror
        #  Requires
        #    n/a
        #  Guarantees
        #    The path to the matching mirror is returned

        source_string = 'source' if source else 'backup'
        mirror_path = os.path.join(self.path, source_string)

        if not os.path.exists(mirror_path):
            raise FileNotFoundError('Mirror does not exist in sandbox')

        return mirror_path           

    def make_library(self, library_name: str, source: bool):
        #  Description
        #    Make a 'library' directory in the matching mirror
        #    Return a path to the directory
        #  Requires
        #    The 'mirror' directory must already exist
        #  Guarantees
        #    The 'library' directory is created and returned

        mirror_path = self.get_mirror_path(source)
        library_path = os.path.join(mirror_path, library_name)

        if os.path.exists(library_path):
            raise FileExistsError('Library already exists in mirror')

        os.mkdir(library_path)
        return MockLibrary(
            name = library_name,
            path = library_path,
            source = source
        )
            
    def make_media(self, media_name: str, file_text: str, mock_library: MockLibrary):
        #  Description
        #    Make a mock 'media file' directory in the matching library
        #    Return an object containing:
        #     - media_name (path_in_library)
        #     - absolute file path
        #     - checksum
        #  Requires
        #    The 'library' must already exist
        #  Guarantees
        #    The mock 'media file' is created and returned

        media_path = os.path.join(mock_library.path, media_name)

        if os.path.exists(media_path):
            raise FileExistsError('Media already exists in library')

        os.makedirs(os.path.dirname(media_path), exist_ok=True)
        with open(media_path, 'w') as new_file:
            new_file.write(file_text)

        return MockMediaFile(
            name = media_name,
            path = media_path,
            library_name = mock_library.name,
            source = mock_library.source
        )

    def populate_library_with_unique_media(self, mock_library: MockLibrary):
        #  Description
        #    Add 12 files to the target library
        #    These files will not exist in the other/mirror library
        #    Return a list of MockMediaFile objects
        #  Requires
        #    The 'library' directory must already exist
        #    This method is only run once per 'library'
        #  Guarantees
        #    12 files will be added to the library in various directories
        #    A list of 12 MockMediaFile objects is returned

        source_string = 'source' if mock_library.source else 'backup'

        return [
            self.make_media('{}-1.mkv'.format(source_string), '{}-1'.format(source_string), mock_library),
            self.make_media('{}-2.mkv'.format(source_string), '{}-2'.format(source_string), mock_library),
            self.make_media('{0}-dir-1/{0}-3.mkv'.format(source_string), '{}-3'.format(source_string), mock_library),
            self.make_media('{0}-dir-1/{0}-4.mkv'.format(source_string), '{}-4'.format(source_string), mock_library),
            self.make_media('{0}-dir-2/{0}-5.mkv'.format(source_string), '{}-5'.format(source_string), mock_library),
            self.make_media('{0}-dir-2/{0}-6.mkv'.format(source_string), '{}-6'.format(source_string), mock_library),
            self.make_media('{0}-dir-2/dir-2.1/{0}-7.mkv'.format(source_string), '{}-7'.format(source_string), mock_library),
            self.make_media('{0}-dir-2/dir-2.1/{0}-8.mkv'.format(source_string), '{}-8'.format(source_string), mock_library),
            self.make_media('{0}-3/dir-3.1/dir-3.1.1/{0}-9.mkv'.format(source_string), '{}-9'.format(source_string), mock_library),
            self.make_media('{0}-3/dir-3.1/dir-3.1.1/{0}-10.mkv'.format(source_string), '{}-10'.format(source_string), mock_library),
            self.make_media('{0}-3/dir-3.1/dir-3.1.2/{0}-11.mkv'.format(source_string), '{}-11'.format(source_string), mock_library),
            self.make_media('{0}-3/dir-3.1/dir-3.1.2/{0}-12.mkv'.format(source_string), '{}-12'.format(source_string), mock_library)
        ]

    def populate_libraries_with_identical_media(self, source_mock_library: MockLibrary, backup_mock_library: MockLibrary):
        #  Description
        #    Add 6 files to the target library, in both mirrors
        #    Return a tuple; two lists of MockMediaFile objects
        #  Requires
        #    The 'library' directories must already exist
        #    This method is only run once per 'library'
        #  Guarantees
        #    6 files will be added to each library in various directories
        #    A tuple is returned:
        #     - The first item is a list of MockMediaFile objects added to the souce library
        #     - The second item is a list of MockMediaFile objects added to the backup library

        source_media = [
            self.make_media('mock-1.mkv', 'mock-1', source_mock_library),
            self.make_media('dir-1/mock-2.mkv', 'mock-2', source_mock_library),
            self.make_media('dir-2/mock-3.mkv', 'mock-3', source_mock_library),
            self.make_media('dir-2/dir-2.1/mock-4.mkv', 'mock-4', source_mock_library),
            self.make_media('dir-3/dir-3.1/dir-3.1.1/mock-5.mkv', 'mock-5', source_mock_library),
            self.make_media('dir-3/dir-3.1/dir-3.1.2/mock-6.mkv', 'mock-6', source_mock_library)
        ]

        backup_media = [
            self.make_media('mock-1.mkv', 'mock-1', backup_mock_library),
            self.make_media('dir-1/mock-2.mkv', 'mock-2', backup_mock_library),
            self.make_media('dir-2/mock-3.mkv', 'mock-3', backup_mock_library),
            self.make_media('dir-2/dir-2.1/mock-4.mkv', 'mock-4', backup_mock_library),
            self.make_media('dir-3/dir-3.1/dir-3.1.1/mock-5.mkv', 'mock-5', backup_mock_library),
            self.make_media('dir-3/dir-3.1/dir-3.1.2/mock-6.mkv', 'mock-6', backup_mock_library)
        ]

        return source_media, backup_media
