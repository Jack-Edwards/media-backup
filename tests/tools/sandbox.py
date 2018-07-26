import os
import shutil
import tempfile

class Sandbox(object):
    def __init__(self):
        self.path = None

        #  Mirrors
        self.mirror_paths = {
            'source': None,
            'backup': None
        }

        #  Standard libraries
        self.library_paths = {
            'Videos': None,
            'TV Shows': None,
            'Music': None
        }

        #  Media files and directories that exist in both mirrors
        #  Do not modify this dict; it is just a template
        self.mirrored_media_file_paths = {
            'mock.mkv': None,
            'mock.mp3': None,
            'mock.mp4': None,
            'dir-1/mock.mkv': None,
            'dir-1/dir-1/mock.mkv': None,
            'dir-2/mock-1.mkv': None,
            'dir-2/mock-2.mkv': None,
        }

        #  Inherit media files and directories from 'self.mirrored_media_file_paths'
        self.source_media_file_paths = self.mirrored_media_file_paths
        self.backup_media_file_paths = self.mirrored_media_file_paths

        #  Add source-specific files and directories
        self.source_media_file_paths['source.mkv'] = None
        self.source_media_file_paths['source.mp3'] = None
        self.source_media_file_paths['dir-1/source.mkv'] = None
        self.source_media_file_paths['source/source.mkv'] = None

        #  Add backup-specific files and directories
        self.backup_media_file_paths['backup.mkv'] = None
        self.backup_media_file_paths['backup.mp3'] = None
        self.backup_media_file_paths['dir-1/backup.mkv'] = None
        self.backup_media_file_paths['backup/backup.mkv'] = None

    def create(self):
        #  Description
        #    Create a temporary directory for unit tests to run in
        #  Requires
        #    n/a
        #  Guarantees
        #    Temporary directory is created and set to 'self.path'

        if self.path:
            raise FileExistsError('Sandbox already exists')
        else:
            self.path = tempfile.mkdtemp()

    def create_all(self):
        #  Description
        #    Create an entire sandbox, including mirrors, libraries, and media files
        #  Requires
        #    n/a
        #  Guarantees
        #    Sandbox dir is made
        #    Mirrors dirs are made (2)
        #    Library dirs are made (3 in each mirror)
        #    Media files are made (4 in each library)

        if self.path:
            raise FileExistsError('Sandbox already exists')
        else:
            self.create()

        #  Make mirror directories
        self.mirror_paths['source'] = self.make_mirror_directory(True)
        self.mirror_paths['backup'] = self.make_mirror_directory(False)

        #  Put library directories in each mirror
        for mirror_type in self.mirror_paths.keys():
            for library_name in self.library_paths.keys():
                self.library_paths[library_name] = self.make_library_directory(library_name, mirror_type == 'source')
                if mirror_type == 'source':
                    for file_path in self.source_media_file_paths.keys():
                        self.source_media_file_paths[file_path] = self.make_media_file(file_path, library_name)
                else:
                    for file_path in self.backup_media_file_paths.keys():
                        self.backup_media_file_paths[file_path] = self.make_media_file(file_path, library_name)

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

    def make_mirror_directory(self, mirror_type):
        #  Description
        #    Create a directory directly under 'self.path' to mimic a mirror
        #  Requires
        #    'mirror_type' is a key 'self.mirror_paths'
        #  Guarantees
        #    The directory is created and it's path is returned
       
        mirror_path = os.path.join(self.path, mirror_type)
        if os.path.exists(mirror_path):
            raise FileExistsError('Mirror already exists in sandbox')
        else:
            os.mkdir(mirror_path)
        
        return mirror_path

    def make_library_directory(self, name, mirror_type):
        #  Description
        #    Make a library directory directly under a mirror directory
        #  Requires
        #    'name' must be string
        #    'mirror_type' is a key 'self.mirror_paths'
        #  Guarantees
        #    A directory of 'name' is created under the mirror directory
        
        library_path = os.path.join(self.mirror_paths[mirror_type], name)
        if os.path.exists(library_path):
            raise FileExistsError('Library already exists in mirror')
        else:
            os.mkdir(library_path)
        return library_path

    def make_media_file(self, name, library_name):
        #  Description
        #    Make a media in the desired library
        #  Requires
        #    'name' is a string filename with/out a relative path pre-pended
        #    'library_name' is a key in 'self.library_paths'
        #  Guarantees
        #    A media file is created in the library
        #    Any directories passed in with 'name' are created

        file_path = os.path.join(self.library_paths[library_name], name)
        if os.path.exists(file_path):
            raise FileExistsError('File already exists in library')
        else:
            os.makedirs(file_path)
        return file_path