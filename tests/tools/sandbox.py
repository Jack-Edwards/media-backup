import hashlib
import os
import shutil
import tempfile

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

        self.source_mirror = self.make_mirror(True)
        self.source_video_library = self.make_library('Videos', True)
        self.source_music_library = self.make_library('Music', True)

        self.backup_mirror = self.make_mirror(False)
        self.backup_video_library = self.make_library('Videos', False)
        self.backup_video_library = self.make_library('Music', False)

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

    def make_mirror(self, is_source):
        #  Description
        #    Make a 'mirror' directory in the sandbox
        #    Return a path to the directory
        #  Requires
        #    'self.path' must exist on the disc
        #  Guarantees
        #    The 'mirror' directory is created and returned

        source_string = 'source' if is_source else 'backup'
        mirror_path = os.path.join(self.path, source_string)

        if os.path.exists(mirror_path):
            raise FileExistsError('Mirror already exists in sandbox')

        os.mkdir(mirror_path)
        return mirror_path

    def get_mirror(self, is_source):
        #  Description
        #    Get the path to the matching mirror
        #  Requires
        #    n/a
        #  Guarantees
        #    The path to the matching mirror is returned

        source_string = 'source' if is_source else 'backup'
        mirror_path = os.path.join(self.path, source_string)

        if not os.path.exists(mirror_path):
            raise FileNotFoundError('Mirror does not exist in sandbox')

        return mirror_path           

    def make_library(self, library_name, is_source):
        #  Description
        #    Make a 'library' directory in the matching mirror
        #    Return a path to the directory
        #  Requires
        #    The 'mirror' directory must already exist
        #  Guarantees
        #    The 'library' directory is created and returned

        mirror_path = self.get_mirror(is_source)
        library_path = os.path.join(mirror_path, library_name)

        if os.path.exists(library_path):
            raise FileExistsError('Library already exists in mirror')

        os.mkdir(library_path)
        return library_path

    def get_library(self, library_name, is_source):
        #  Description
        #    Get the path to the matching library in the matching mirror
        #  Requires
        #    n/a
        #  Guarantees
        #    The path to the matching library is returned

        mirror_path = self.get_mirror(is_source)
        if not os.path.exists(mirror_path):
            raise FileNotFoundError('Mirror does not exist in sandbox')

        library_path = os.path.join(mirror_path, library_name)
        if not os.path.exists(library_path):
            raise FileNotFoundError('Library does not exist in mirror')

        return library_path
            
    def make_media(self, media_name, file_text, library_name, is_source):
        #  Description
        #    Make a mock 'media file' directory in the matching library
        #    Return an object containing:
        #     - media_name (path_in_library)
        #     - absolute file path
        #     - checksum
        #  Requires
        #    The 'library' directory must already exist
        #  Guarantees
        #    The mock 'media file' is created and returned

        library_path = self.get_library(library_name, is_source)
        media_path = os.path.join(library_path, media_name)

        if os.path.exists(media_path):
            raise FileExistsError('Media already exists in library')

        os.makedirs(os.path.dirname(media_path), exist_ok=True)
        with open(media_path, 'w') as new_file:
            new_file.write(file_text)

        return MockMediaFile(
            name = media_name,
            path = media_path,
            library_name = library_name,
            is_source = is_source
        )

class MockMediaFile(object):
    def __init__(self, name, path, library_name, is_source):
        self.name = name
        self.path = path
        self.library_name = library_name
        self.is_source = is_source
