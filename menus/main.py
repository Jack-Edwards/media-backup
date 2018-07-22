def run(manager):
    while True:
        manual_count = manager.manual_problem_count
        automatic_count = manager.automatic_problem_count
        input_string = (
            '=== Main Menu ===' +
            '\n1. Perform automatic maintenance ({})'.format(automatic_count) +
            '\n2. View items needing attention ({})'.format(manual_count) +
            '\n3. Process items needing attention ({})'.format(manual_count) +
            '\n9. Refresh' +
            '\n0. Exit' +
            '\nChoose option: '
        )

        result = input(input_string)
        if result == '1':
            manager.process_stale_cache_files()
            manager.process_new_source_media()
            manager.process_orphan_cache_files()
            manager.process_empty_directories()
        elif result == '2':
            print(
                '> Local checksum errors: {}'.format(manager.media_with_local_checksum_error_count) +
                '\n> Mirror checksum errors: {}'.format(manager.media_with_mirror_checksum_error_count) +
                '\n> Orphan backup files: {}'.format(manager.orphan_backup_media_count)
            )
        elif result == '3':
            manager.process_local_checksum_errors()
            manager.process_mirror_checksum_errors()
            manager.process_orphan_backup_media()
        elif result == '9':
            manager.load_mirror_libraries()
        elif result == '0':
            exit()