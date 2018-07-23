# Media-Backup
Command-line interface to help backup and maintain your media libraries.

## Intended Use-Cases
* Automatically. backup new files from the 'source' location to the 'backup' location
* Automatically perform 'safe' maintenance operations, including removal of empty directories.
* Automatically verify the integrity of a media file has not changed since the last backup.
* Get notified when the integrity of a media file has changed and choose how to proceed.
    * This may be due to a newer version of the media file, in which case the CLI can be instructed to overwrite the backup file.
    * This may also be due to file corruption, in which case the CLI can be instructed to restore from the backup file.

## Invalid Use-Cases
* Run the CLI as a cron job or scheduled task.
* Keep the CLI running in the background.

## Getting Started
1. Download the project files to the computer where your 'source' media files are located.
2. Verify the 'backup' disc is connected to the computer.
3. Open 'config.json'.  Edit these settings:
    * **source_path** is the absolute path to the directory containing the 'source' media files
    * **backup_path** is the absolute path to the 'backup' directory where all 'source' files will be copied to
    * **libraries** is a list of directories under the **source_path**
    * Examples:
        1. Backing up from a Linux PC to USB drive:
            * **source_path** = "/home/<user>"
            * **libraries** = [ "Music", "Videos" ]
            * **backup_path** = "/media/<user>/BACKUP USB"
4. Open a terminal or command window.  Use "cd" to navigate to the directory **above** the Media-Backup project folder.
5. Run this command to run Media-Backup using Python 3.5 or higher:
    * python -m media-backup.run
    * /or/
    * python3 -m media-backup.run
6. Media-Backup performs a startup scan.  Every path in **libraries** must exist in the **source_path** location.  A directory will be created for each path in **libraries** that does not exist in **backup_path**.  All libraries under **source_path** and **backup_path** are scanned for media files.
7. The main menu will appear.  If this is the first time running Media-Backup, choose option 1 to perform automatic maintenance.  This will:
    * Backup media files from **source_path** libraries to **backup_path** libraries if they do not exist in **backup_path** libraries.
    * Remove empty directories from each library for both **source_path** and **backup_path**.
8. After automatic maintenance completes, the main menu will appear again.  Choose option 0 to exit Media-Backup.

## Keep Backing Up
* Regularly run Media-Backup to backup new media files and verify the integrity of media files that have already been backed up.
* If Media-Backup detects a file integrity issue, options 2 and 3 in the main menu will have a number (other than "0") next to them.  Use option 2 to view the problems.  Use option 3 to resolve the problems.

## Tested Environments
* Debian 9.4 - Stretch using Python 3.5+
* Ubuntu 16.04 - Xenial using Python 3.5+

## Run Unit Tests
* python3 -m media-backup.tests.run_tests