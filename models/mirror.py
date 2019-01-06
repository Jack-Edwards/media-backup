import os
from .library import Library

class BaseMirror(object):
    def __init__(self, path: str, source: bool):
        self.path = path
        self.source = source
        self.libraries = dict()  # {'library_name': LibraryObject}
        self.exists = os.path.exists(self.path)

        #  The mirror must exist
        assert self.exists, 'Mirror does not exist: {}'.format(self.path)

    def load_library(self, library):
        #  Append a Library object to 'self.libraries'
        #  This does not load any of the library's media

        library_path = os.path.join(self.path, library)

        #  The library must exist if this is the "source"
        library_exists = os.path.exists(library_path)
        library_is_backup = not self.source
        assert (library_exists or library_is_backup), 'Library does not exist on source: {}'.format(library_path)

        #  Make the library path if it does not exist
        if not library_exists:
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
