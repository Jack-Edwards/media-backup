import os

from .library import Library

class BaseMirror(object):
    def __init__(self, path: str, source: bool):
        self.path = path
        self.source = source
        self.libraries = dict()  # {'library_name': LibraryObject}

        if not os.path.exists(self.path):
            raise FileNotFoundError('Mirror path does not exist')

    def load_library(self, library):
        library_path = os.path.join(self.path, library)

        #  The library must exist if this is the "source" mirror
        if not os.path.exists(library_path):
            if self.source:
                raise FileNotFoundError('Library path does not exist on source')
            else:
                os.makedirs(library_path)
        
        #  Add the library object to 'self.libraries' as {'library_name': LibraryObject}
        self.libraries[library] = Library(
            name=library,
            path=library_path,
            source=self.source
        )


class SourceMirror(BaseMirror):
    def __init__(self, path):
        BaseMirror.__init__(self, path=path, source=True)

class BackupMirror(BaseMirror):
    def __init__(self, path):
        BaseMirror.__init__(self, path=path, source=False)

class MirrorManager(object):
    def __init__(self, source_path, backup_path, libraries):
        self.source_mirror = SourceMirror(source_path)
        self.backup_mirror = BackupMirror(backup_path)
        self.libraries = libraries
        self.mirrors_loaded = False

    @property
    def total_problem_count(self):
        return (
            self.source_media_not_backed_up_count +
            self.orphan_backup_media_count +
            self.media_with_stale_cache_count +
            self.media_with_local_checksum_error_count +
            self.orphan_cache_file_count +
            self.empty_directory_count +
            self.media_with_mirror_checksum_error_count
        )

    @property
    def automatic_problem_count(self):
        return (
            self.source_media_not_backed_up_count +
            self.media_with_stale_cache_count +
            self.orphan_cache_file_count +
            self.empty_directory_count
        )

    @property
    def manual_problem_count(self):
        return (
            self.orphan_backup_media_count +
            self.media_with_local_checksum_error_count +
            self.media_with_mirror_checksum_error_count
        )

    @property
    def orphan_cache_file_count(self):
        count = 0
        for _ in self.yield_orphan_cache_files():
            count += 1
        return count

    @property
    def empty_directory_count(self):
        count = 0
        for _ in self.yield_empty_directories():
            count += 1
        return count

    @property
    def source_media_not_backed_up_count(self):
        count = 0
        for _ in self.yield_source_media_not_backed_up():
            count += 1
        return count

    @property
    def orphan_backup_media_count(self):
        count = 0
        for _ in self.yield_orphan_backup_media():
            count += 1
        return count

    @property
    def media_with_stale_cache_count(self):
        count = 0
        for _ in self.yield_media_with_stale_cache():
            count += 1
        return count

    @property
    def media_with_local_checksum_error_count(self):
        count = 0
        for _ in self.yield_media_with_local_checksum_error():
            count += 1
        return count

    @property
    def media_with_mirror_checksum_error_count(self):
        count = 0
        for _ in self.yield_media_with_mirror_checksum_error():
            count += 1
        return count

    def load_mirrors(self):
        for library in self.libraries:
            self.source_mirror.load_library(library)
        for library in self.libraries:
            self.backup_mirror.load_library(library)
        self.mirrors_loaded = True

    def load_mirror_libraries(self):
        for library in self.libraries:
            self.source_mirror.libraries[library].load_all_media()
        for library in self.libraries:
            self.backup_mirror.libraries[library].load_all_media()

    def yield_source_media_not_backed_up(self):
        if self.mirrors_loaded:
            for library in self.libraries:
                for path_in_library in self.source_mirror.libraries[library].media:
                    if path_in_library not in self.backup_mirror.libraries[library].media:
                        yield library, path_in_library
        else:
            raise BaseException('Mirrors not loaded')

    def yield_orphan_backup_media(self):
        if self.mirrors_loaded:
            for library in self.libraries:
                for path_in_library in self.backup_mirror.libraries[library].media:
                    if path_in_library not in self.source_mirror.libraries[library].media:
                        yield library, path_in_library
        else:
            raise BaseException('Mirrors not loaded')

    #  This method gets tricky.  Hurdles:
    #  - Each file has a real_checksum and cache_checksum.  Which values to compare?
    #  - What if there is a local checksum mismatch?
    #  Answer:
    #  - Compare the checksum values; calculating the real checksum for every file is going to take too long
    #  - Trust that user/script knows to resolve local checksum errors before tackling mirror checksum errors
    def yield_media_with_mirror_checksum_error(self):
        if self.mirrors_loaded:
            for library in self.libraries:
                for path_in_library in self.source_mirror.libraries[library].media:
                    source_media = self.source_mirror.libraries[library].media[path_in_library]

                    #  Verify the media also exists on the backup
                    if path_in_library in self.backup_mirror.libraries[library].media:
                        if source_media.cached_checksum != self.backup_mirror.libraries[library].media[path_in_library].cached_checksum:
                            yield 'source', library, path_in_library
                #  Do not repeat for backup mirror
                #  By definition, it's' impossible for a mirror checksum error to exist /just/ on the backup
        else:
            raise BaseException('Mirrors not loaded')

    def yield_media_with_stale_cache(self):
        if self.mirrors_loaded:
            for library in self.libraries:
                for path_in_library in self.source_mirror.libraries[library].media:
                    source_media = self.source_mirror.libraries[library].media[path_in_library]
                    if source_media.cache_is_stale:
                        yield 'source', library, path_in_library
                for path_in_library in self.backup_mirror.libraries[library].media:
                    backup_media = self.backup_mirror.libraries[library].media[path_in_library]
                    if backup_media.cache_is_stale:
                        yield 'backup', library, path_in_library
        else:
            raise BaseException('Mirrors not loaded')

    def yield_media_with_local_checksum_error(self):
        if self.mirrors_loaded:
            for library in self.libraries:
                for path_in_library in self.source_mirror.libraries[library].media:
                    source_media = self.source_mirror.libraries[library].media[path_in_library]
                    if source_media.real_checksum != source_media.cached_checksum:
                        yield 'source', library, path_in_library
                for path_in_library in self.backup_mirror.libraries[library].media:
                    backup_media = self.backup_mirror.libraries[library].media[path_in_library]
                    if backup_media.real_checksum != backup_media.cached_checksum:
                        yield 'backup', library, path_in_library
        else:
            raise BaseException('Mirrors not loaded')

    def yield_empty_directories(self):
        if self.mirrors_loaded:
            mirrors = [
                self.source_mirror,
                self.backup_mirror
            ]
            for mirror in mirrors:
                for library in self.libraries:
                    path = mirror.libraries[library].path
                    for dirpath, dirnames, filenames in os.walk(path):
                        if len (dirnames) == 0 and len(filenames) == 0:
                            yield dirpath
        else:
            raise BaseException('Mirrors not loaded')

    def yield_orphan_cache_files(self):
        if self.mirrors_loaded:
            mirrors = [
                self.source_mirror,
                self.backup_mirror
            ]
            for mirror in mirrors:
                for library in self.libraries:
                    path = mirror.libraries[library].path
                    for dirpath, _, filenames in os.walk(path):
                        if '.cache' in dirpath:
                            if len(filenames) > 0:
                                for file in filenames:
                                    parent_dir = os.path.dirname(dirpath)
                                    media_file_name = os.path.splitext(file)[0]
                                    media_file = os.path.join(parent_dir, media_file_name)
                                    if not os.path.exists(media_file):
                                        yield os.path.join(dirpath, file)
        else:
            raise BaseException('Mirrors not loaded')

    #  Automatic processing
    def process_stale_cache_files(self):
        if self.mirrors_loaded:
            for mirror, library, path_in_library in self.yield_media_with_stale_cache():
                if mirror.lower() == 'source':
                    media = self.source_mirror.libraries[library].media[path_in_library]
                elif mirror.lower() == 'backup':
                    media = self.backup_mirror.libraries[library].media[path_in_library]
                else:
                    raise ValueError('Unexpected mirror value')
                if media.real_checksum == media.cached_checksum:
                    media.save_checksum_to_file(overwrite=True)
        else:
            raise BaseException('Mirrors not loaded')

    #  Automatic processing
    def process_empty_directories(self):
        if self.mirrors_loaded:
            directories = list()
            for directory in self.yield_empty_directories():
                directories.append(directory)

            for directory in directories:
                print(directory)
                os.rmdir(directory)
        else:
            raise BaseException('Mirrors not loaded')

    #  Automatic processing
    def process_orphan_cache_files(self):
        if self.mirrors_loaded:
            files = list()
            for file in self.yield_orphan_cache_files():
                files.append(file)

            for file in files:
                os.remove(file)
        else:
            raise BaseException('Mirrors not loaded')

    #  Automatic processing
    #  This is safe to do before fixing checksum errors
    def process_new_source_media(self):
        if self.mirrors_loaded:
            for library, path_in_library in self.yield_source_media_not_backed_up():
                media = self.source_mirror.libraries[library].media[path_in_library]
                if media.real_checksum == media.cached_checksum:
                    self.backup_mirror.libraries[library].copy_media(media.path, media.path_in_library, media.real_checksum)
        else:
            raise BaseException('Mirrors not loaded')

    #  This could be automatic, but I want to make it require user input
    def process_orphan_backup_media(self):
        if self.mirrors_loaded:
            #  Unfortunately, deleting an orphan media breaks the generator,
            #  so need to create a local collection and iterate over that instead
            orphan_media = list()
            for library, path_in_library in self.yield_orphan_backup_media():
                orphan_media.append({
                    'library': library,
                    'path_in_library': path_in_library
                })

            for orphan in orphan_media:
                library = orphan['library']
                path_in_library = orphan['path_in_library']
                while True:
                    print('> Orphaned backup file: {}/{}'.format(
                        library,
                        path_in_library
                    ))

                    input_string = (
                        '1. Delete the file.' +
                        '\n2. Restore the file'
                        '\n3. Skip for now.' +
                        '\nChoose an option: '
                    )
                    result = input(input_string)

                    if result == '1':
                        self.backup_mirror.libraries[library].delete_media(path_in_library)
                        break
                    if result == '2':
                        backup_media = self.backup_mirror.libraries[library].media[path_in_library]
                        self.source_mirror.libraries[library].copy_media(backup_media.path, path_in_library, backup_media.real_checksum)
                        break
                    elif result == '3':
                        break
        else:
            raise BaseException('Mirrors not loaded')

    #  This requires user input
    def process_local_checksum_errors(self):
        if self.mirrors_loaded:
            for mirror, library, path_in_library in self.yield_media_with_local_checksum_error():
                while True:
                    print('> Local checksum error: [{}]/{}/{}'.format(
                        mirror,
                        library,
                        path_in_library
                    ))

                    #  Determine which mirror this media belongs to
                    if mirror is 'source':
                        this_mirror = self.source_mirror
                        other_mirror = self.backup_mirror
                    else:
                        this_mirror = self.backup_mirror
                        other_mirror = self.source_mirror

                    #  Determine whether the media exists on the other mirror
                    if path_in_library in other_mirror.libraries[library].media:
                        mirror_media = other_mirror.libraries[library].media[path_in_library]
                    else:
                        mirror_media = None

                    input_string = (
                        '1. File is valid. Update local cache.' +
                        '\n2. File is corrupt. Restore from mirror.' +
                        '\n3. Skip for now.' +
                        '\nChoose an option: '
                    )
                    result = input(input_string)

                    if result == '1':
                        #  The file is valid.  Update the cache file with the new checksum
                        this_mirror.libraries[library].media[path_in_library].save_checksum_to_file(overwrite=True)
                        this_mirror.libraries[library].media[path_in_library].load_checksum_from_file()
                        break
                    elif result == '2':
                        #  The file is not valid.  Delete the file then copy from other mirror
                        if mirror_media:
                            #  The file exists on the other mirror.  Proceed
                            this_mirror.libraries[library].delete_media(path_in_library)
                            this_mirror.libraries[library].copy_media(mirror_media.path, path_in_library, mirror_media.real_checksum)
                            break
                        else:
                            #  The file does not exist on the other mirror
                            #  Tell the user and let the user act
                            print('Error: File does not exist in Backup mirror')
                            # Don't break
                    elif result == '3':
                        #  Skip this file
                        break
        else:
            raise BaseException('Mirrors not loaded')

    #  This requires user input
    def process_mirror_checksum_errors(self):
        if self.mirrors_loaded:
            for mirror, library, path_in_library in self.yield_media_with_mirror_checksum_error():
                while True:
                    print('> Mirror checksum error: [{}]/{}/{}'.format(
                        mirror,
                        library,
                        path_in_library)
                    )

                    input_string = (
                        '1. Source file is correct. Overwrite backup file.' +
                        '\n2. Backup file is correct. Overwrite source file.' +
                        '\n3. Skip for now.'
                        '\nChoose an option: '
                    )
                    result = input(input_string)

                    if result == '1':
                        # Source file is good; overwrite backup file
                        good_media = self.source_mirror.libraries[library].media[path_in_library]
                        if os.path.exists(good_media.path):
                            self.backup_mirror.libraries[library].delete_media(path_in_library)
                            self.backup_mirror.libraries[library].copy_media(good_media.path, path_in_library, good_media.real_checksum)
                        else:
                            print('Error: Files does not exists in Backup')
                            # Don't break
                        break
                    elif result == '2':
                        # Backup file is good; overwrite source file
                        good_media = self.backup_mirror.libraries[library].media[path_in_library]
                        if os.path.exists(good_media.path):
                            self.source_mirror.libraries[library].delete_media(path_in_library)
                            self.source_mirror.libraries[library].copy_media(good_media.path, path_in_library, good_media.real_checksum)
                        else:
                            print('Error: File does not exist in Source')
                            # Don't break
                        break
                    elif result == '3':
                        break
        else:
            raise BaseException('Mirrors not loaded')
