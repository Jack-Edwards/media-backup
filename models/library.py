import os
import shutil

from .mediafile import MediaFile

class Library(object):
    def __init__(self, name, source, path):
        self.name = name
        self.source = source
        self.path = path
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

    #  Populate 'self.media' with all media files in the library
    def load_all_media(self):
        #  Verify the library's path exists
        if os.path.exists(self.path):
            self.media.clear()  # Reset 'self.media'; old entries might no longer exist
            for dirpath, dirnames, filenames in os.walk(self.path):
                if '.cache' not in dirpath:
                    if len(filenames) > 0:
                        for filename in filenames:
                            if os.path.splitext(filename)[1] in self.allowed_media_extensions:
                                filepath = os.path.join(dirpath, filename)
                                filepath_in_library = filepath.replace(self.path + os.sep, '')
                                self.media[filepath_in_library] = MediaFile(filepath, filepath_in_library, self.source)
        else:
            raise FileNotFoundError('Library path does not exist')

    #  Copy a file into the library
    def copy_media(self, source_filepath, path_in_library, source_hash):
        #  Verify the file exists
        if os.path.exists(source_filepath):
            destination_filepath= os.path.join(self.path, path_in_library)
            if os.path.exists(destination_filepath):
                raise FileExistsError('File already exists in library')
            else:
                #  Make missing directories
                if not os.path.exists(os.path.dirname(destination_filepath)):
                    os.makedirs(os.path.dirname(destination_filepath))

                #  Copy from source to destination
                shutil.copy2(source_filepath, destination_filepath)

                #  Add the library object to 'self.libraries' as {'path_in_library': MediaFileObject}
                self.media[path_in_library] = MediaFile(destination_filepath, path_in_library, self.source)

                #  Verify the source and copied files' filehashes match
                if self.media[path_in_library].real_hash == source_hash:
                    self.media[path_in_library].save_hash_to_file(overwrite=True)
                    self.media[path_in_library].load_hash_from_file()
                else:
                    raise IOError('Filehashes do not match')
        else:
            raise FileNotFoundError('File does not exist')

    def delete_media(self, path_in_library):
        #  Verify the file exists
        file = self.media[path_in_library]
        if os.path.exists(file.path):
            os.remove(file.cache_file)
            os.remove(file.path)
            self.media.pop(path_in_library)
        else:
            raise FileNotFoundError('File does not exist')
