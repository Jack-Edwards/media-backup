import os
import shutil
from functools import wraps

from .media_file import MediaFile
from .result import Result

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

    def backup_only(function):
        @wraps(function)
        def function_wrapper(inst, *args, **kwargs):
            assert not inst.source
            return function(inst, *args, **kwargs)
        return function_wrapper

    def source_only(function):
        @wraps(function)
        def function_wrapper(inst, *args, **kwargs):
            assert inst.source
            return function(inst, *args, **kwargs)
        return function_wrapper

    def load_all_media(self, callback_on_progress):
        #  Description
        #    Populate 'self.media' with all media files in the library
        #  Requires
        #    'self.path' must exist on the filesystem
        #  Guarantees
        #    All media files with 'allowed_media_extensions' are added to 'self.media'

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
                        if callback_on_progress:
                            callback_on_progress(
                                mirror_is_source=self.source,
                                library_name=self.name,
                                current_media_count=len(self.media)
                            )
        return True

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
                return Result(
                    subject=source_filepath,
                    success=False,
                    message='Media already exists in library.'
                )
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
                    self.media[path_in_library].save_cache_file(overwrite=False)
                    self.media[path_in_library].load_cache_file()
                    return Result(subject=source_filepath, success=True)
                else:
                    #  Something went wrong, undo the copy
                    copied_file_checksum = self.media[path_in_library].real_checksum
                    self.delete_media(path_in_library)
                    return Result(
                        subject=source_filepath,
                        success=False,
                        message=(
                            'Checksums for source file and copied file do not match.' +
                            '\nThe copied file has been deleted.' +
                            '\nSource file checksum: {}'.format(source_checksum) +
                            '\nCopied file checksum: {}'.format(copied_file_checksum)
                        )
                    )
        else:
            return Result(
                subject=source_filepath,
                success=False,
                message='Source file does not exist.'
            )

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
        assert os.path.exists(media_file.path)
        if os.path.exists(media_file.cache_file):
            os.remove(media_file.cache_file)
        os.remove(media_file.path)
        self.media.pop(path_in_library)

    def get_empty_directories(self):
        #  Description
        #    Get all empty directories in the library
        #  Requires
        #    'self.path' must exist on the filesystem
        #  Guarantees
        #    The path to all empty directories in 'self.path' is returned in the form of a list

        list_of_empty_directories = []
        for dirpath, dirnames, filenames in os.walk(self.path):
            if len(dirnames) == 0 and len(filenames) == 0:
                #  Don't delete the library itself
                if dirpath is not self.path:
                    list_of_empty_directories.append(dirpath)
        return list_of_empty_directories

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
            empty_directories = self.get_empty_directories()
            if len(empty_directories) > 0:
                for directory in empty_directories:
                    os.rmdir(directory)
            else:
                break

    def get_orphan_cache_files(self):
        #  Description
        #    Get all orphan cache files in the library
        #  Requires
        #    'self.path' must exist on the filesystem
        #  Guarantees
        #    The path to all orphan cache files in 'self.path' is returned in the form of a list

        list_of_orphan_cache_files = []
        for dirpath, _, filenames in os.walk(self.path):
            if '.cache' in dirpath:
                for cache_file in filenames:
                    if os.path.splitext(cache_file)[1] == '.txt':
                        parent_directory = os.path.dirname(dirpath)
                        media_file_name = os.path.splitext(cache_file)[0]
                        media_file_path = os.path.join(parent_directory, media_file_name)
                        if not os.path.exists(media_file_path):
                            list_of_orphan_cache_files.append(os.path.join(dirpath, cache_file))
        return list_of_orphan_cache_files

    def delete_orphan_cache_files(self):
        #  Description
        #    Delete all cache files without a matching media file in the library
        #  Requires
        #    'self.path' must exist on the filesystem
        #  Guarantees
        #    All orphan cache files under 'self.path' are removed from the disc

        for cache_file in self.get_orphan_cache_files():
            os.remove(cache_file)

    def get_stale_cache_media(self, stale_cache_days):
        stale_cache_media = []
        for path_in_library in self.media:
            if self.media[path_in_library].cache_is_stale(stale_cache_days):
                stale_cache_media.append(path_in_library)
        return stale_cache_media
        
    def refresh_stale_cache_files(self, stale_cache_days, callback_on_start, callback_on_progress):
        stale_cache_media = self.get_stale_cache_media(stale_cache_days)
        if callback_on_start:
            callback_on_start(
                mirror_is_source=self.source,
                total_files_to_refresh=len(stale_cache_media),
                library_name=self.name
            )
        for index, path_in_library in enumerate(stale_cache_media):
            if callback_on_progress:
                callback_on_progress(
                    total_files_to_refresh=len(stale_cache_media),
                    file_number=index + 1,
                    mirror_is_source=self.source,
                    file_name=path_in_library,
                    library_name=self.name
                )
            media = self.media[path_in_library]
            if media.real_checksum == media.cached_checksum:
                media.refresh_cache_file()

    def get_local_checksum_discrepancies(self, cache_days):
        local_checksum_discrepancies = []
        for path_in_library in self.get_stale_cache_media(cache_days):
            media = self.media[path_in_library]
            if media.real_checksum != media.cached_checksum:
                local_checksum_discrepancies.append(path_in_library)
        return local_checksum_discrepancies

    @source_only
    def get_mirror_checksum_discrepancies(self, backup_library):
        mirror_checksum_discrepancies = []
        for path_in_library in self.media:
            if backup_library[path_in_library]:
                source_media = self.media[path_in_library]
                backup_media = backup_library.media[path_in_library]
                if source_media.cached_checksum != backup_media.cached_checksum:
                    mirror_checksum_discrepancies.append(path_in_library)
        return mirror_checksum_discrepancies

    @backup_only
    def get_media_not_backed_up(self, source_library):
        list_of_media_not_backed_up = []
        for path_in_library in source_library.media:
            if path_in_library not in self.media:
                list_of_media_not_backed_up.append(path_in_library)
        return list_of_media_not_backed_up

    @backup_only
    def backup_new_media(self, source_library, callback_on_start, callback_on_progress, callback_on_error):
        media_to_backup = self.get_media_not_backed_up(source_library)
        #  Callback on start of method
        if callback_on_start:
            callback_on_start(
                total_files_to_backup=len(media_to_backup),
                library_name=self.name
            )
        for index, path_in_library in enumerate(media_to_backup):
            if path_in_library not in self.media:
                #  Callback on new file to backup
                if callback_on_progress:
                    callback_on_progress(
                        total_files_to_backup=len(media_to_backup),
                        file_number=index + 1,
                        file_name=path_in_library,
                        library_name=self.name
                    )
                source_media = source_library.media[path_in_library]
                copy_result = self.copy_media(
                    source_filepath=source_media.path,
                    path_in_library=path_in_library,
                    source_checksum=source_media.real_checksum
                )
                #  Handle copy failure
                if callback_on_error:
                    if not copy_result.success:
                        callback_on_error(
                            file_name=path_in_library,
                            library_name=self.name,
                            error_message=copy_result.message
                        )
