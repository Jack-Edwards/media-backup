import os
import shutil

from .mediafile import MediaFile

class Library(object):
    def __init__(self, name, source, path):
        self.name = name
        self.source = source
        self.path = path
        self.media = dict()  # {'path_in_library': MediaFileObject}

        self.allowed_media_extensions = [
            '.3gpp',
            '.asf',
            '.avi',
            '.flac',
            '.flv',
            '.m2ts',
            '.m4a',
            '.m4v',
            '.mka',
            '.mkv',
            '.mov',
            '.mp3',
            '.mp4',
            '.mpeg-ts',
            '.mpegts',
            '.ogg',
            '.ts',
            '.wav',
            '.wma',
            '.wtv'
        ]

    #  Populate 'self.media' with all media files in the library
    def load_all_media(self):
        #  Verify the library's path exists
        if os.path.exists(self.path):
            self.media.clear()  # Reset 'self.media'; old entries might no longer exist
            for dirpath, _, filenames in os.walk(self.path):
                if '.cache' not in dirpath:
                    if len(filenames) > 0:
                        for filename in filenames:
                            if os.path.splitext(filename)[1] in self.allowed_media_extensions:
                                filepath = os.path.join(dirpath, filename)
                                filepath_in_library = filepath.replace(self.path + os.sep, '')
                                self.media[filepath_in_library] = MediaFile(filepath, filepath_in_library, self.source)
        else:
            raise FileNotFoundError('Library path does not exist')

    #  Copy a file into the library
    def copy_media(self, source_filepath, path_in_library, source_hash):
        #  Verify the file exists
        if os.path.exists(source_filepath):
            destination_filepath= os.path.join(self.path, path_in_library)
            if os.path.exists(destination_filepath):
                raise FileExistsError('File already exists in library')
            else:
                #  Make missing directories
                if not os.path.exists(os.path.dirname(destination_filepath)):
                    os.makedirs(os.path.dirname(destination_filepath))

                #  Copy from source to destination
                shutil.copy2(source_filepath, destination_filepath)

                #  Add the library object to 'self.libraries' as {'path_in_library': MediaFileObject}
                self.media[path_in_library] = MediaFile(destination_filepath, path_in_library, self.source)

                #  Verify the source and copied files' filehashes match
                if self.media[path_in_library].real_hash == source_hash:
                    self.media[path_in_library].save_hash_to_file(overwrite=True)
                    self.media[path_in_library].load_hash_from_file()
                else:
                    raise IOError('Filehashes do not match')
        else:
            raise FileNotFoundError('File does not exist')

    def delete_media(self, path_in_library):
        #  Description
        #    Delete a media file from the library
        #  Requires
        #    'path_in_library' must be a key in 'self.media'
        #  Guarantees
        #    The media file is removed from the filesystem
        #    The media file's cache file is removed from the filesystem, if it exists
        #    The reference to the media file is removed from 'self.media'
        #  Implementation Notes
        #    The method allows media to be deleted from 'source' libraries
        #    This is a necessary step when restoring a file from 'backup'
        #    The 'source' file must be deleted before copying from 'backup'

        #  Verify the file exists
        file = self.media[path_in_library]
        if os.path.exists(file.path):
            if os.path.exists:
                os.remove(file.cache_file)
            os.remove(file.path)
            self.media.pop(path_in_library)
        else:
            raise FileNotFoundError('File does not exist')

    def delete_empty_directories(self):
        #  Description
        #    Delete all empty directories in the library
        #  Requires
        #    'self.path' must exist on the filesystem
        #  Guarantees
        #    All empty directories under 'self.path' are removed from the disc
        #    An 'empty' directory has no files or sub-directories
        #  Implementation Notes
        #    Reason for the 'while' loop is for case where deleting a directory
        #    creates an empty directory
        
        while True:
            empty_directories = list()
            for dir in self.yield_empty_directories():
                empty_directories.append(dir)

            if len(empty_directories) > 0:
                for dir in empty_directories:
                    os.rmdir(dir)
            else:
                break       

    def yield_empty_directories(self):
        #  Description
        #    A generator to return the path of all empty directories in the library
        #  Requires
        #    'self.path' must exist on the filesystem
        #    A directory is not removed or added until the generator is finished
        #  Guarantees
        #    The path to all empty directories in 'self.path' is returned, one at a time

        for dirpath, dirnames, filenames in os.walk(self.path):
            if len (dirnames) == 0 and len(filenames) == 0:
                yield dirpath

    def delete_orphan_cache_files(self):
        pass