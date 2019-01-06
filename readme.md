# Media-Backup
Command-line interface to help backup and maintain your media libraries.

## Intended Use-Cases
* Automatically backup new files from the 'source' location to the 'backup' location
* Automatically perform 'safe' maintenance operations, including removal of empty directories.
* Automatically verify the integrity of a media file has not changed since the last backup.
* Get notified when the integrity of a media file has changed and choose how to proceed.
    * This may be due to a newer version of the media file, in which case the CLI can be instructed to overwrite the backup file with the newer file.
    * This may also be due to file corruption, in which case the CLI can be instructed to restore the file from backup.

## Invalid Use-Cases
* Run the CLI as a cron job or scheduled task.
* Manually update files or directories while Media-Backup is running.

## Getting Started
1. Download the project files to the computer where your 'source' media files are located.
2. Verify the 'backup' disc is connected to the computer.
3. Open 'config.json'.  Edit these settings:
    * **source_path** is the absolute path to the directory containing the 'source' media files
    * **backup_path** is the absolute path to the 'backup' directory where all 'source' files will be copied to
    * **libraries** is a list of directories under the **source_path**
    * Examples:
        1. Backing up from a Linux PC to USB drive:
            * **source_path** = "/home/\<user\>"
            * **libraries** = [ "Music", "Videos" ]
            * **backup_path** = "/media/\<user\>/BACKUP USB"
4. Open a terminal or command window.  Use "cd" to navigate to the directory **above** the Media-Backup project folder.
5. Run this command to run Media-Backup using Python 3.5 or higher:
    * python -m media-backup.run
    * /or/
    * python3 -m media-backup.run
6. The main menu will appear.

## Keep Backing Up
* Regularly run Media-Backup to backup new media files and verify the integrity of media files that have already been backed up.

## Tested Environments
* Debian 9.4 - Stretch using Python 3.5+
* Ubuntu 16.04 - Xenial using Python 3.5+

## Run Unit Tests
* python3 -m media-backup.tests.run_tests