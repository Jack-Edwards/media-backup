def run(manager):
    while True:
        input_string = (
            '=== Main Menu ===' +
            '\n1. Backup new source media ({})'.format(manager.source_media_not_backed_up_count) +
            '\n2. (Source) Refresh stale cache files ({})'.format(len(manager.source_mirror.media_with_stale_cache_file)) +
            '\n3. (Backup) Refresh stale cache files ({})'.format(len(manager.backup_mirror.media_with_stale_cache_file)) +
            '\n4. (Source) Resolve local checksum discrepancies ({})'.format(len(manager.source_mirror.media_with_local_checksum_discrepancy)) +
            '\n5. (Backup) Resolve local checksum discrepancies ({})'.format(len(manager.backup_mirror.media_with_local_checksum_discrepancy)) +
            '\n6. Resolve mirror checksum discrepancies ({})'.format(manager.mirror_checksum_discrepancy_count) +
            '\n9. Refresh' +
            '\n0. Exit' +
            '\nChoose option: '
        )

        result = input(input_string)
        if result == '1':
            manager.backup_new_source_media()
        elif result == '2':
            manager.source_mirror.refresh_stale_cache_files()
        elif result == '3':
            manager.backup_mirror.refresh_stale_cache_files()
        elif result == '4':
            manager.process_source_local_checksum_discrepancies()
        elif result == '5':
            manager.process_backup_local_checksum_discrepancies()
        elif result == '6':
            manager.process_mirror_checksum_discrepancies()
        elif result == '9':
            manager.load_mirror_libraries()
        elif result == '0':
            exit()