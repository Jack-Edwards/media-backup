import os
import shutil

from .media_file import MediaFile

class Library(object):
    def __init__(self, name: str, path: str, source: bool):
        self.name = name
        self.path = path
        self.source = source
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

    def load_all_media(self):
        #  Description
        #    Populate 'self.media' with all media files in the library
        #  Requires
        #    'self.path' must exist on the filesystem
        #  Guarantees
        #    All media files with 'allowed_media_extensions_ are added to 'self.media'

        #  Reset 'self.media'
        #  Old members may no longer exist
        self.media.clear()

        #  Populate 'self.media'
        for dirpath, _, filenames in os.walk(self.path):
            if '.cache' not in dirpath:
                for filename in filenames:
                    if os.path.splitext(filename)[1] in self.allowed_media_extensions:
                        filepath = os.path.join(dirpath, filename)
                        filepath_in_library = filepath.replace(self.path + os.sep, '')
                        self.media[filepath_in_library] = MediaFile(filepath, filepath_in_library, self.source)

    def copy_media(self, source_filepath, path_in_library, source_checksum):
        #  Description
        #    Copy a media file into the library from an outside location
        #  Requires
        #    'self.path' must exist on the filesystem
        #    'source_filepath' must exist on the filesystem
        #    'path_in_library' must not already exist in the library
        #    'source_checksum' must match the checksum for the file in 'source_filepath'
        #  Guarantees
        #    The file will be copied in to the library under 'path_in_library'
        #    The file will have cache_file generated in the library
        #    The copied file will be added to 'self.media' as 'self.media[path_in_library]'
        #    If the checksum match fails, the copied file is deleted from the library

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

                #  Add the library object to 'self.media' as {'path_in_library': MediaFileObject}
                self.media[path_in_library] = MediaFile(destination_filepath, path_in_library, self.source)

                #  Verify the source and copied files' checksums match
                if self.media[path_in_library].real_checksum == source_checksum:
                    self.media[path_in_library].save_checksum_to_cache(overwrite=False)
                    self.media[path_in_library].load_checksum_from_cache()
                else:
                    #  Something went wrong, undo the copy
                    self.delete_media(path_in_library)
                    raise IOError('Checksums did not match')
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
        media_file = self.media[path_in_library]
        if os.path.exists(media_file.path):
            if os.path.exists(media_file.cache_file):
                os.remove(media_file.cache_file)
            os.remove(media_file.path)
            self.media.pop(path_in_library)
        else:
            raise FileNotFoundError('File does not exist')

    def yield_empty_directories(self):
        #  Description
        #    A generator to return the path of all empty directories in the library
        #  Requires
        #    'self.path' must exist on the filesystem
        #    A directory is not added or removed until the generator is finished
        #  Guarantees
        #    The path to all empty directories in 'self.path' is returned, one at a time

        for dirpath, dirnames, filenames in os.walk(self.path):
            if len(dirnames) == 0 and len(filenames) == 0:
                yield dirpath

    def delete_empty_directories(self):
        #  Description
        #    Delete all empty directories in the library
        #    A list of deleted directories is returned
        #  Requires
        #    'self.path' must exist on the filesystem
        #  Guarantees
        #    All empty directories under 'self.path' are removed from the disc
        #    An 'empty' directory has no files or sub-directories
        #    A list of deleted directories is returned
        #  Implementation Notes
        #    Reason for the 'while' loop is for case where deleting a directory
        #    creates an empty directory
        
        deleted_directories = list()
        while True:
            empty_directories = list()
            for directory in self.yield_empty_directories():
                empty_directories.append(directory)

            if len(empty_directories) > 0:
                for directory in empty_directories:
                    os.rmdir(directory)
                    deleted_directories.append(directory)
            else:
                break
        
        return deleted_directories

    def yield_orphan_cache_files(self):
        #  Description
        #    A generator to return the path of all cache files without
        #    a matching media file in the library
        #  Requires
        #    'self.path' must exist on the filesystem
        #    A cache file is not added or removed until the generator is finished
        #  Guarantees
        #    The path to all orphan cache files in 'self.path' is returned, one at a time

        for dirpath, _, filenames in os.walk(self.path):
            if '.cache' in dirpath:
                for cache_file in filenames:
                    parent_directory = os.path.dirname(dirpath)
                    media_file_name = os.path.splitext(cache_file)[0]
                    media_file_path = os.path.join(parent_directory, media_file_name)
                    if not os.path.exists(media_file_path):
                        yield os.path.join(dirpath, cache_file)

    def delete_orphan_cache_files(self):
        #  Description
        #    Delete all cache files without a matching media file in the library
        #    A list of deleted files is returned
        #  Requires
        #    'self.path' must exist on the filesystem
        #  Guarantees
        #    All orphan cache files under 'self.path' are removed from the disc
        #    The list of deleted files is returned

        orphan_cache_files = list()
        for cache_file in self.yield_orphan_cache_files():
            orphan_cache_files.append(cache_file)

        for cache_file in orphan_cache_files:
            os.remove(cache_file)
        
        return orphan_cache_files

    def yield_media_with_stale_cache_file(self):
        #  Description
        #    A generator to return a MediaFile object for media files with
        #    stale cache/checksum files
        #  Requires
        #    'self.path' must exist on the filesystem
        #    'self.load_all_media()' has been called and 'self.media' is populated
        #    A media file is not added or removed until the generator is finished
        #  Guarantees
        #    A MediaFile object is returned for each media file with a stale
        #    cache/checksum file, one at a time

        for media_file in self.media.values():
            if media_file.cache_is_stale():
                yield media_file

    def refresh_stale_cache_files(self):
        #  Description
        #    Set today's date in old cache files
        #    Return a list of media_files with real and
        #    cached checksum discrepancies
        #  Requires
        #    'self.path' must exist on the filesystem
        #    'self.load_all_media()' has been called and 'self.media' is populated
        #  Guarantees
        #    Old cache files will have today's date set, if the media_file's
        #    real_checksum matches it's cached_checksum
        #    If the media_file's checksums do not match, it will be returned
        #    in a list

        media_files_with_checksum_discrepancies = list()
        for media_file in self.yield_media_with_stale_cache_file():
            if media_file.real_and_cached_checksums_match:
                media_file.refresh_checksum()
            else:
                media_files_with_checksum_discrepancies.append(media_file)

        return media_files_with_checksum_discrepancies