def run(manager):
    while True:
        orphan_cache_file_count = (
            manager.source_mirror.orphan_cache_file_count +
            manager.backup_mirror.orphan_cache_file_count
        )
        empty_directory_count = (
            manager.source_mirror.empty_directory_count +
            manager.backup_mirror.empty_directory_count
        )
        input_string = (
            '=== Main Menu ===' +
            '\n1. Backup new source media ({})'.format(manager.source_media_not_backup_up_count) +
            '\n2. (Source) Refresh stale cache files ({})'.format(len(manager.source_mirror.media_with_stale_cache_file)) +
            '\n3. (Backup) Refresh stale cache files ({})'.format(len(manager.backup_mirror.media_with_stale_cache_file)) +
            '\n4. (Source) Resolve local checksum discrepancies ({})'.format(len(manager.source_mirror.media_with_local_checksum_discrepancy)) +
            '\n5. (Backup) Resolve local checksum discrepancies ({})'.format(len(manager.backup_mirror.media_with_local_checksum_discrepancy)) +
            '\n6. Resolve mirror checksum discrepancies ({})'.format(manager.mirror_checksum_discrepancy_count) +
            '\n7. Delete orphan cache files ({})'.format(orphan_cache_file_count) +
            '\n8. Delete empty directories ({})'.format(empty_directory_count) +
            '\n9. Refresh' +
            '\n0. Exit' +
            '\nChoose option: '
        )

        result = input(input_string)
        print('')
        if result == '1':
            for new_source_media in manager.backup_new_source_media():
                print('Backing up: {}'.format(new_source_media))
        elif result == '2':
            for media_with_stale_cache in manager.source_mirror.refresh_stale_cache_files():
                print('Refreshing cache: {}'.format(media_with_stale_cache))
        elif result == '3':
            for media_with_stale_cache in manager.backup_mirror.refresh_stale_cache_files():
                print('Refreshing cache: {}'.format(media_with_stale_cache))
        elif result == '4':
            manager.process_source_local_checksum_discrepancies()
        elif result == '5':
            manager.process_backup_local_checksum_discrepancies()
        elif result == '6':
            manager.process_mirror_checksum_discrepancies()
        elif result == '7':
            deleted_source_files = manager.source_mirror.delete_orphan_cache_files()
            deleted_backup_files = manager.backup_mirror.delete_orphan_cache_files()
            deleted_files = deleted_source_files + deleted_backup_files
            for deleted_file in deleted_files:
                print('Deleted file: {}'.format(deleted_file))
        elif result == '8':
            deleted_source_directories = manager.source_mirror.delete_empty_directories()
            deleted_backup_directories = manager.backup_mirror.delete_empty_directories()
            deleted_directories = deleted_source_directories + deleted_backup_directories
            for deleted_directory in deleted_directories:
                print('Deleted directory: {}'.format(deleted_directory))
        elif result == '9':
            manager.load_mirror_libraries()
        elif result == '0':
            exit()
        print('')