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

    @property
    def media_with_stale_cache_file(self):
        media_with_stale_cache_file = list()
        for library in self.libraries.values():
            for media in library.yield_media_with_stale_cache_file():
                media_with_stale_cache_file.append(media)
        return media_with_stale_cache_file

    @property
    def empty_directory_count(self):
        count = 0
        for library in self.libraries.values():
            for _ in library.yield_empty_directories():
                count += 1
        return count

    @property
    def orphan_cache_file_count(self):
        count = 0
        for library in self.libraries.values():
            for _ in library.yield_orphan_cache_files():
                count += 1
        return count

    @property
    def media_with_local_checksum_discrepancy(self):
        media_with_local_checksum_discrepancy = list()
        for library in self.libraries.values():
            for media in library.yield_media_with_local_checksum_discrepancy():
                media_with_local_checksum_discrepancy.append(media)
        return media_with_local_checksum_discrepancy

    def refresh_stale_cache_files(self):
        for library in self.libraries.values():
            for media_with_stale_cache in library.refresh_stale_cache_files():
                yield media_with_stale_cache

    def delete_empty_directories(self):
        deleted_directories = list()
        for library in self.libraries.values():
            deleted_directories += library.delete_empty_directories()
        return deleted_directories

    def delete_orphan_cache_files(self):
        deleted_files = list()
        for library in self.libraries.values():
            deleted_files += library.delete_orphan_cache_files()
        return deleted_files

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
    def source_media_not_backup_up_count(self):
        count = 0
        for _ in self.yield_source_media_not_backed_up():
            count += 1
        return count

    @property
    def mirror_checksum_discrepancy_count(self):
        count = 0
        for _ in self.yield_media_with_mirror_checksum_discrepancy():
            count += 1
        return count

    @property
    def orphan_backup_media_count(self):
        count = 0
        for _ in self.yield_orphan_backup_media():
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

    #  This is safe to do before fixing checksum discrepancies
    def backup_new_source_media(self):
        if self.mirrors_loaded:
            for library, path_in_library in self.yield_source_media_not_backed_up():
                media = self.source_mirror.libraries[library].media[path_in_library]
                if media.real_checksum == media.cached_checksum:
                    yield media.path
                    self.backup_mirror.libraries[library].copy_media(media.path, media.path_in_library, media.real_checksum)
        else:
            raise BaseException('Mirrors not loaded')

    #  This requires user input
    def process_source_local_checksum_discrepancies(self):
        if self.mirrors_loaded:
            for library_name in self.source_mirror.libraries:
                source_media_files = list(media for media in self.source_mirror.libraries[library_name].yield_media_with_local_checksum_discrepancy())
                for source_media_file in source_media_files:
                    while True:
                        print('> Local checksum discrepancy: {}'.format(source_media_file.path) + 
                            '\n > Real checksum: {}'.format(source_media_file.real_checksum) + 
                            '\n > Cached checksum: {}'.format(source_media_file.cached_checksum)
                        )

                        input_string = (
                            '1. File is valid. Update the local cache file with new checksum value.' +
                            '\n2. Print the backup file\'s checksum values.' +
                            '\n3. File is not valid.  Overwrite this file with file from backup.' +
                            '\n4. Skip for now.' +
                            '\nChoose an option: '
                        )
                        result = input(input_string)

                        #  Determine whether the media exists on the backup mirror
                        path_in_library = source_media_file.path_in_library
                        if path_in_library in self.backup_mirror.libraries[library_name].media:
                            backup_media_file = self.backup_mirror.libraries[library_name].media[path_in_library]
                        else:
                            backup_media_file = None

                        if result == '1':
                            #  The file is valid.  Update the cache file with the new checksum
                            source_media_file.save_checksum_to_file(overwrite=True)
                            source_media_file.load_checksum_from_file()
                            break
                        elif result == '2':
                            if backup_media_file:
                                print('> Backup file: {}'.format(backup_media_file.path) + 
                                    '\n > Real checksum: {}'.format(backup_media_file.real_checksum) + 
                                    '\n > Cached checksum: {}'.format(backup_media_file.cached_checksum)
                                )
                            else:
                                print('> Backup file not found.')
                        elif result == '3':
                            if backup_media_file:
                                #  todo - instead of deleting the media, put the media in a temp location
                                #         that way the delete can be undone if the copy goes bad
                                self.source_mirror.libraries[library_name].delete_media(path_in_library)
                                self.source_mirror.libraries[library_name].copy_media(
                                    backup_media_file.path,
                                    path_in_library,
                                    backup_media_file.real_checksum
                                )
                                break
                            else:
                                print('> Backup file not found.')
                        elif result == '4':
                            break
        else:
            raise BaseException('Mirrors not loaded')

    def process_backup_local_checksum_discrepancies(self):
        if self.mirrors_loaded:
            for library_name in self.backup_mirror.libraries:
                backup_media_files = list()
                for media_file in self.backup_mirror.libraries[library_name].yield_media_with_local_checksum_discrepancy():
                    backup_media_files.append(media_file)

                for backup_media_file in backup_media_files:
                    while True:
                        print('> Local checksum discrepancy: {}'.format(backup_media_file.path) + 
                            '\n > Real checksum: {}'.format(backup_media_file.real_checksum) + 
                            '\n > Cached checksum: {}'.format(backup_media_file.cached_checksum)
                        )

                        input_string = (
                            '1. File is valid. Update the local cache file with new checksum value.' +
                            '\n2. Print the source file\'s checksum values.' +
                            '\n3. File is not valid.  Overwrite this file with file from source.' +
                            '\n4. Skip for now.' +
                            '\nChoose an option: '
                        )
                        result = input(input_string)

                        #  Determine whether the media exists on the source mirror
                        path_in_library = backup_media_file.path_in_library
                        if path_in_library in self.source_mirror.libraries[library_name].media:
                            source_media_file = self.backup_mirror.libraries[library_name].media[path_in_library]
                        else:
                            source_media_file = None

                        if result == '1':
                            #  The file is valid.  Update the cache file with the new checksum
                            backup_media_file.save_checksum_to_file(overwrite=True)
                            backup_media_file.load_checksum_from_file()
                            break
                        elif result == '2':
                            if source_media_file:
                                print('> Source file: {}'.format(source_media_file.path) + 
                                    '\n > Real checksum: {}'.format(source_media_file.real_checksum) + 
                                    '\n > Cached checksum: {}'.format(source_media_file.cached_checksum)
                                )
                            else:
                                print('> Source file not found.')
                        elif result == '3':
                            if source_media_file:
                                #  todo - instead of deleting the media, put the media in a temp location
                                #         that way the delete can be undone if the copy goes bad
                                self.backup_mirror.libraries[library_name].delete_media(path_in_library)
                                self.backup_mirror.libraries[library_name].copy_media(
                                    source_media_file.path,
                                    path_in_library,
                                    source_media_file.real_checksum
                                )
                                break
                            else:
                                print('> Source file not found.')
                        elif result == '4':
                            break
        else:
            raise BaseException('Mirrors not loaded')

    #  - Compare the checksum values; calculating the real checksum for every file is going to take too long
    #  - Trust that user/script knows to resolve local checksum errors before tackling mirror checksum errors
    def yield_media_with_mirror_checksum_discrepancy(self):
        if self.mirrors_loaded:
            for library_name in self.source_mirror.libraries:
                for path_in_library in self.source_mirror.libraries[library_name].media:
                    source_media = self.source_mirror.libraries[library_name].media[path_in_library]

                    #  Verify the media also exists on the backup
                    if path_in_library in self.backup_mirror.libraries[library_name].media:
                        backup_media = self.backup_mirror.libraries[library_name].media[path_in_library]
                        if source_media.cached_checksum != backup_media.cached_checksum:
                            yield {
                                'library_name': library_name,
                                'source_media': source_media,
                                'backup_media': backup_media
                            }
                    else:
                        pass  #  There is nothing to verify
            #  Do not repeat for backup mirror
            #  By definition, it's' impossible for a mirror checksum error to exist /just/ on the backup
        else:
            raise BaseException('Mirrors not loaded')

    #  This requires user input
    def process_mirror_checksum_discrepancies(self):
        if self.mirrors_loaded:
            mirror_checksum_discrepancies = list(media for media in self.yield_media_with_mirror_checksum_discrepancy())
            for media_with_mirror_checksum_discrepancy in mirror_checksum_discrepancies:
                while True:
                    library_name = media_with_mirror_checksum_discrepancy['library_name']
                    source_media = media_with_mirror_checksum_discrepancy['source_media']
                    backup_media = media_with_mirror_checksum_discrepancy['backup_media']
                    path_in_library = source_media.path_in_library

                    print('> Mirror checksum discrepancy: {}>{}'.format(library_name, path_in_library) + 
                        '\n > Source real checksum:   {}'.format(source_media.real_checksum) + 
                        '\n > Source cached checksum: {}'.format(source_media.cached_checksum) +
                        '\n > Backup real checksum:   {}'.format(backup_media.real_checksum) +
                        '\n > Backup cached checksum: {}'.format(backup_media.cached_checksum)
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
                        self.backup_mirror.libraries[library_name].delete_media(path_in_library)
                        self.backup_mirror.libraries[library_name].copy_media(source_media.path, path_in_library, source_media.real_checksum)
                        break
                    elif result == '2':
                        # Backup file is good; overwrite source file
                        self.source_mirror.libraries[library_name].delete_media(path_in_library)
                        self.source_mirror.libraries[library_name].copy_media(backup_media.path, path_in_library, backup_media.real_checksum)
                        break
                    elif result == '3':
                        break
        else:
            raise BaseException('Mirrors not loaded')

    def yield_orphan_backup_media(self):
        if self.mirrors_loaded:
            for library_name in self.source_mirror.libraries:
                for path_in_library in self.backup_mirror.libraries[library_name].media:
                    if path_in_library not in self.source_mirror.libraries[library_name].media:
                        yield {
                            'library_name': library_name,
                            'path_in_library': path_in_library
                        }
        else:
            raise BaseException('Mirrors not loaded')

    #  This could be automatic, but I want to make it require user input
    def process_orphan_backup_media(self):
        if self.mirrors_loaded:
            orphan_backup_media = list(media for media in self.yield_orphan_backup_media())
            for orphan in orphan_backup_media:
                library_name = orphan['library_name']
                path_in_library = orphan['path_in_library']
                while True:
                    print('> Orphan backup file: {}/{}'.format(
                        library_name,
                        path_in_library
                    ))

                    input_string = (
                        '1. Delete the file' +
                        '\n2. Restore the file' +
                        '\n3. Skip for now' +
                        '\nChoose an option: '
                    )
                    result = input(input_string)

                    if result == '1':
                        self.backup_mirror.libraries[library_name].delete_media(path_in_library)
                        break
                    elif result == '2':
                        backup_media = self.backup_mirror.libraries[library_name].media[path_in_library]
                        self.source_mirror.libraries[library_name].copy_media(backup_media.path, path_in_library, backup_media.real_checksum)
                        break
                    elif result == '3':
                        break
        else:
            raise BaseException('Mirrors not loaded')