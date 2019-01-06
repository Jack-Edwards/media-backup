import threading
import time
from functools import wraps
from ..models import MediaFile
from ..models import SourceMirror
from ..models import BackupMirror

class MainController(object):
    def __init__(self, source_path, backup_path, libraries, stale_cache_days):
        self.source_path = source_path
        self.backup_path = backup_path
        self.source_mirror = None
        self.backup_mirror = None
        self.libraries = libraries
        self.stale_cache_days = stale_cache_days

    def require_mirrors_are_loaded(function):
        #  Decorator to ensure mirrors are loaded
        #  Ignore pylint errors
        #  Reference: https://stackoverflow.com/a/13852431

        @wraps(function)
        def function_wrapper(inst, *args, **kwargs):
            assert inst.source_mirror is not None, 'Source mirror is not loaded'
            assert inst.backup_mirror is not None, 'Backup mirror is not loaded'
            return function(inst, *args, **kwargs)
        return function_wrapper

    def require_no_local_checksum_discrepancies(function):
        @wraps(function)
        def function_wrapper(inst, *args, **kwargs):
            assert len(inst.get_media_with_local_checksum_discrepancy()) is 0
            return function(inst, *args, **kwargs)
        return function_wrapper

    def quick_scan(self):
        self.backup_new_source_media()

    def regular_scan(self):
        self.backup_new_source_media()
        print('')
        self.refresh_stale_cache_files(self.stale_cache_days)
        print('')
        self.delete_orphan_cache_files()

    def full_scan(self):
        self.backup_new_source_media()
        print('')
        self.refresh_stale_cache_files(-1)
        print('')
        self.delete_orphan_cache_files()

    def load_mirrors(self):
        self.load_mirror(is_source=True, mirror_path=self.source_path)
        self.load_mirror(is_source=False, mirror_path=self.backup_path)
        print('')

    def load_mirror(self, is_source, mirror_path):
        if is_source:
            self.source_mirror = SourceMirror(mirror_path)
            mirror = self.source_mirror
        else:
            self.backup_mirror = BackupMirror(mirror_path)
            mirror = self.backup_mirror

        for library_name in self.libraries:
            mirror.load_library(library_name)
            self.on_load_library_progress(
                mirror_is_source=is_source,
                library_name=library_name,
                current_media_count=0
            )
            mirror.libraries[library_name].load_all_media(self.on_load_library_progress)
            print('')

    def on_load_library_progress(self, mirror_is_source, library_name, current_media_count):
        print('Loading {0} library "{1}":  {2}'.format(
            'source' if mirror_is_source else 'backup',
            library_name,
            current_media_count
        ), end='\r')

    @require_mirrors_are_loaded
    def backup_new_source_media(self):
        for library_name in self.libraries:
            #  Have the backup mirror scan the source mirror for new media files
            #  The backup mirror will copy over any new media files
            self.backup_mirror.libraries[library_name].backup_new_media(
                source_library=self.source_mirror.libraries[library_name],
                callback_on_start=self.on_backup_start,
                callback_on_progress=self.on_backup_progress,
                callback_on_error=self.on_backup_error
            )

    def on_backup_start(self, total_files_to_backup, library_name):
        print('{0} new media files in library "{1}"'.format(total_files_to_backup, library_name))

    def on_backup_progress(self, total_files_to_backup, file_number, file_name, library_name):
        print('Backing up {0}/{1}: [{2}: {3}]'.format(file_number, total_files_to_backup, library_name, file_name))

    def on_backup_error(self, file_name, library_name, error_message):
        print('An error occurred during backup: [{0}: {1}]'.format(library_name, file_name))
        print(error_message)
        exit()

    @require_mirrors_are_loaded
    def refresh_stale_cache_files(self, days_until_stale):
        for library_name in self.libraries:
            self.source_mirror.libraries[library_name].refresh_stale_cache_files(
                stale_cache_days=days_until_stale,
                callback_on_start=self.on_refresh_start,
                callback_on_progress=self.on_refresh_progress
                )
            if len(self.source_mirror.libraries[library_name].media) > 0:
                print('')
            self.backup_mirror.libraries[library_name].refresh_stale_cache_files(
                stale_cache_days=days_until_stale,
                callback_on_start=self.on_refresh_start,
                callback_on_progress=self.on_refresh_progress
            )
            if len(self.backup_mirror.libraries[library_name].media) > 0:
                print('')
     
    def on_refresh_start(self, mirror_is_source, total_files_to_refresh, library_name):
        print('{0} media files with stale cache files in {1} library "{2}"'.format(
            total_files_to_refresh,
            'source' if mirror_is_source else 'backup',
            library_name
        ))

    def on_refresh_progress(self, total_files_to_refresh, file_number, mirror_is_source, file_name, library_name):
        print(' > Refreshing cache file {0}/{1}: [{2}/{3}: {4}]'.format(
            file_number,
            total_files_to_refresh,
            'Source' if mirror_is_source else 'Backup',
            library_name,
            file_name
        ), end='\r')

    @require_mirrors_are_loaded
    def delete_orphan_cache_files(self):
        print('Deleting orphan cache files...')
        for library in list(self.source_mirror.libraries.values()) + list(self.backup_mirror.libraries.values()):
            library.delete_orphan_cache_files()

    @require_mirrors_are_loaded
    def get_orphan_backup_media(self):
        orphan_backup_media = []
        for library_name in self.libraries:
            for path_in_library in self.backup_mirror.libraries[library_name].media:
                if path_in_library not in self.source_mirror.libraries[library_name].media:
                    orphan_backup_media.append({
                        'library_name': library_name,
                        'path_in_library': path_in_library
                    })
        return orphan_backup_media

    @require_mirrors_are_loaded
    def delete_orphan_backup_media(self):
        for orphan_backup_media in self.get_orphan_backup_media():
            library_name = orphan_backup_media['library_name']
            path_in_library = orphan_backup_media['path_in_library']
            input('Enter to delete: {}/{}'.format(library_name, path_in_library))
            self.backup_mirror.libraries[library_name].delete_media(path_in_library)

    @require_mirrors_are_loaded
    def get_empty_directory_count(self):
        count = 0
        for library in self.source_mirror.libraries.values():
            count += len(library.get_empty_directories())
        for library in self.backup_mirror.libraries.values():
            count += len(library.get_empty_directories())
        return count

    @require_mirrors_are_loaded
    def delete_empty_directories(self):
        for library in self.source_mirror.libraries.values():
            library.delete_empty_directories()
        for library in self.backup_mirror.libraries.values():
            library.delete_empty_directories()

    def print_message_while_thread_is_alive(self, message, thread):
        ellipsis_count = 3
        thread_started = False
        while thread.is_alive() or thread_started is False:
            ellipsis_string = '.' * ellipsis_count
            empty_space = ' ' * (3 - ellipsis_count)
            print('{}{}{}'.format(message, ellipsis_string, empty_space), end='\r')
            if not thread_started:
                thread.start()
                thread_started = True
            ellipsis_count += 1
            if ellipsis_count > 3:
                ellipsis_count = 0

    @require_mirrors_are_loaded
    def get_media_with_local_checksum_discrepancy(self):
        #  Check all media with stale cache files for a local checksum discrepancy
        #  Media with fresh cache files are not checked
        media_with_local_checksum_discrepancy = []
        for library_name in self.libraries:
            source_and_backup_media_in_library = (
                list(self.source_mirror.libraries[library_name].media.values()) + 
                list(self.backup_mirror.libraries[library_name].media.values())
            )
            for media in source_and_backup_media_in_library:
                if media.cache_is_stale(self.stale_cache_days):
                    if media.real_checksum != media.cached_checksum:
                        media_with_local_checksum_discrepancy.append({
                            'source': media.source,
                            'library_name': library_name,
                            'path_in_library': media.path_in_library
                        })
        return media_with_local_checksum_discrepancy

    @require_mirrors_are_loaded
    def resolve_local_checksum_discrepancy(self, is_source, library_name, path_in_library):
        if is_source:
            target_library = self.source_mirror.libraries[library_name]
            target_media = target_library.media[path_in_library]
            if path_in_library in self.backup_mirror.libraries[library_name].media:
                mirror_media = self.backup_mirror.libraries[library_name].media[path_in_library]
            else:
                mirror_media = None
        else:
            target_library = self.backup_mirror.libraries[library_name]
            target_media = target_library.media[path_in_library]
            if path_in_library in self.source_mirror.libraries[library_name].media:
                mirror_media = self.source_mirror.libraries[library_name].media[path_in_library]
            else:
                mirror_media = None

        while True:
            print('> Local checksum discrepancy: {}'.format(target_media.path))
            target_media.print_info()
            two_string = '2. View the mirror file\'s values' if mirror_media else '2'+'\u0336'+'. Mirror file does not exist'
            three_string = '3. File is not valid. Overwrite this file with file from mirror' if mirror_media else '3'+'\u0336'+'. Mirror file does not exist'
            input_string = (
                '1. Media file is valid. Update the local cache file with new values' +
                '\n{0}' +
                '\n{1}' +
                '\n4. Skip' +
                '\nChoose an option: '
            ).format(
                two_string,
                three_string
            )
            result = input(input_string)
            if result is '1':
                #  Refresh the cache file
                print('Updating cache file with new values...')
                target_media.save_cache_file(overwrite=True)
                break
            elif result is '2' and mirror_media:
                #  Print the mirror media's info
                mirror_media.print_info()
            elif result is '3' and mirror_media:
                #  Copy the mirror media to the current library
                print('Overwriting file with file from mirror...')
                target_library.delete_media(path_in_library)
                target_library.copy_media(mirror_media.path, path_in_library, mirror_media.real_checksum)
                break
            elif result is '4':
                break

    @require_mirrors_are_loaded
    def get_media_with_mirror_checksum_discrepancy(self):
        #  Check all source media for a mirror checksum discrepancy
        media_with_mirror_checksum_discrepancy = []
        for library_name in self.libraries:
            for source_media in self.source_mirror.libraries[library_name].media.values():
                path_in_library = source_media.path_in_library

                #  Make sure the backup media actually exists
                if path_in_library in self.backup_mirror.libraries[library_name].media:
                    backup_media = self.backup_mirror.libraries[library_name].media[path_in_library]
                    if backup_media:
                        if source_media.cached_checksum != backup_media.cached_checksum:
                            media_with_mirror_checksum_discrepancy.append({
                                'library_name': library_name,
                                'path_in_library': path_in_library
                            })
        return media_with_mirror_checksum_discrepancy

    @require_mirrors_are_loaded
    @require_no_local_checksum_discrepancies
    def resolve_mirror_checksum_discrepancy(self, library_name, path_in_library):
        source_library = self.source_mirror.libraries[library_name]
        source_media = source_library.media[path_in_library]
        backup_library = self.backup_mirror.libraries[library_name]
        backup_media = backup_library.media[path_in_library]

        while True:
            print('> Mirror checksum discrepancy: {}'.format(path_in_library))
            source_media.print_info()
            print('')
            backup_media.print_info()
            input_string = (
                '1. Source file is valid. Overwrite backup file' +
                '\n2. Backup file is valid. Overwrite source file' +
                '\n3. Skip' +
                '\nChoose an option: '
            )
            result = input(input_string)
            if result is '1':
                #  Delete the backup file and copy the source file to the backup mirror
                backup_library.delete_media(path_in_library)
                backup_library.copy_media(
                    source_filepath=source_media.path,
                    path_in_library=path_in_library,
                    source_checksum=source_media.real_checksum
                )
                break
            elif result is '2':
                #  Delete the source file and copy the backup file to the source mirror
                source_library.delete_media(path_in_library)
                source_library.copy_media(
                    source_filepath=backup_media.path,
                    path_in_library=path_in_library,
                    source_checksum=backup_media.real_checksum
                )
                break
            elif result is '3':
                break