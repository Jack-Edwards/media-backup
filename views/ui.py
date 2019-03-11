import json
import os
import time
from ..controllers import MainController

class UI(object):
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

        #  UI Counts
        self.local_checksum_discrepancy_count = None
        self.mirror_checksum_discrepancy_count = None
        self.orphan_backup_media_count = None
        self.empty_directory_count = None

        #  Main controller
        self.controller = None

    def load_controller(self):
        #  Load settings from file
        config = json.load(open(self.config_file_path))

        #  Load the controller
        self.controller = MainController(
            source_path=config['source_path'],
            backup_path=config['backup_path'],
            libraries=config['libraries'],
            stale_cache_days=config['days_before_cache_is_stale']
        )
        self.controller.load_mirrors()

    def main_menu(self):
        while True:
            input_string = (
                '=== Main Menu ===' +
                '\n1. Quick Scan' +
                '\n2. Regular Scan' +
                '\n3. Full Scan' +
                '\n...' +
                '\n4. Resolve local checksum discrepancies [{0}]' +
                '\n5. Resolve mirror checksum discrepancies [{1}]' +
                '\n6. Delete orphaned media files from backup [{2}]' +
                '\n7. Delete empty directories [{3}]' +
                '\n...' +
                '\n0. Exit' +
                '\nChoose option: '
            ).format(
                'Run Regular/Full Scan to get count' if self.local_checksum_discrepancy_count is None else self.local_checksum_discrepancy_count,
                'Run Regular/Full Scan to get count' if self.mirror_checksum_discrepancy_count is None else self.mirror_checksum_discrepancy_count,
                'Run Regular/Full Scan to get count' if self.orphan_backup_media_count is None else self.orphan_backup_media_count,
                'Run any scan to get count' if self.empty_directory_count is None else self.empty_directory_count
            )
            result = input(input_string)
            if result is '1':
                print('\n=== Quick Scan ===')
                time.sleep(1)
                print('Reloading config: {}\n'.format(self.config_file_path))
                self.load_controller()
                self.controller.quick_scan()
                self.orphan_backup_media_count = len(self.controller.get_orphan_backup_media())
                self.empty_directory_count = self.controller.get_empty_directory_count()
                print('\nScan finished')
                print('')
            elif result is '2':
                print('\n=== Regular Scan ===')
                time.sleep(1)
                print('Reloading config: {}\n'.format(self.config_file_path))
                self.load_controller()
                self.controller.regular_scan()
                self.local_checksum_discrepancy_count = len(self.controller.get_media_with_local_checksum_discrepancy())
                self.mirror_checksum_discrepancy_count = len(self.controller.get_media_with_mirror_checksum_discrepancy())
                self.orphan_backup_media_count = len(self.controller.get_orphan_backup_media())
                self.empty_directory_count = self.controller.get_empty_directory_count()
                print('\nScan finished')
                print('')
            elif result is '3':
                print('\n=== Full Scan ===')
                time.sleep(1)
                print('Reloading config: {}\n'.format(self.config_file_path))
                self.load_controller()
                self.controller.full_scan()
                self.local_checksum_discrepancy_count = len(self.controller.get_media_with_local_checksum_discrepancy())
                self.mirror_checksum_discrepancy_count = len(self.controller.get_media_with_mirror_checksum_discrepancy())
                self.orphan_backup_media_count = len(self.controller.get_orphan_backup_media())
                self.empty_directory_count = self.controller.get_empty_directory_count()
                print('\nScan finished')
                print('')
            elif result is '4':
                print('\n=== Resolve Local Checksum Discrepancies ===')
                time.sleep(1)
                print('Reloading config: {}\n'.format(self.config_file_path))
                self.load_controller()
                self.resolve_local_checksum_discrepancy_menu()
                self.local_checksum_discrepancy_count = len(self.controller.get_media_with_local_checksum_discrepancy())
                self.mirror_checksum_discrepancy_count = len(self.controller.get_media_with_mirror_checksum_discrepancy())
                self.orphan_backup_media_count = len(self.controller.get_orphan_backup_media())
                self.empty_directory_count = self.controller.get_empty_directory_count()
                print('')
            elif result is '5':
                print('\n=== Resolve Mirror Checksum Discrepancies ===')
                time.sleep(1)
                print('Reloading config: {}\n'.format(self.config_file_path))
                self.load_controller()
                self.resolve_mirror_checksum_discrepancy_menu()
                self.local_checksum_discrepancy_count = len(self.controller.get_media_with_local_checksum_discrepancy())
                self.mirror_checksum_discrepancy_count = len(self.controller.get_media_with_mirror_checksum_discrepancy())
                self.orphan_backup_media_count = len(self.controller.get_orphan_backup_media())
                self.empty_directory_count = self.controller.get_empty_directory_count()
                print('')
            elif result is '6':
                print('\n=== Delete Orphan Backup Media ===')
                time.sleep(1)
                print('Reloading config: {}\n'.format(self.config_file_path))
                self.load_controller()
                print('Deleting orphan backup media...')
                self.controller.delete_orphan_backup_media()
                self.local_checksum_discrepancy_count = len(self.controller.get_media_with_local_checksum_discrepancy())
                self.mirror_checksum_discrepancy_count = len(self.controller.get_media_with_mirror_checksum_discrepancy())
                self.orphan_backup_media_count = len(self.controller.get_orphan_backup_media())
                self.empty_directory_count = self.controller.get_empty_directory_count()
                print('')
            elif result is '7':
                print('\n=== Delete Empty Directories ===')
                time.sleep(1)
                print('Reloading config: {}\n'.format(self.config_file_path))
                self.load_controller()
                print('Deleting empty directories...')
                self.controller.delete_empty_directories()
                self.empty_directory_count = self.controller.get_empty_directory_count()
                print('')
            elif result is '0':
                exit()
            else:
                print('')

    def resolve_local_checksum_discrepancy_menu(self):
        local_checksum_discrepancies = self.controller.get_media_with_local_checksum_discrepancy()
        if len(local_checksum_discrepancies) is 0:
            print('No local checksum discrepancies found')
        else:
            for item in local_checksum_discrepancies:
                self.controller.resolve_local_checksum_discrepancy(
                    is_source=item['source'],
                    library_name=item['library_name'],
                    path_in_library=item['path_in_library']
                )

    def resolve_mirror_checksum_discrepancy_menu(self):
        mirror_checksum_discrepancies = self.controller.get_media_with_mirror_checksum_discrepancy()
        if len(mirror_checksum_discrepancies) is 0:
            print('No mirror checksum discrepancies found')
        else:
            for item in self.controller.get_media_with_mirror_checksum_discrepancy():
                self.controller.resolve_mirror_checksum_discrepancy(
                    library_name=item['library_name'],
                    path_in_library=item['path_in_library']
                )
