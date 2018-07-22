import datetime
import json
import os
import sys

from . import menus
from .models import MirrorManager

#  === Begin - Config and Global Variables ===

#  Load config from file`
module_path = os.path.dirname(__file__)
config_path = os.path.join(module_path, 'config.json')
config = json.load(open(config_path))

#  Filesystem config
SOURCE_PATH = config['source_path']
BACKUP_PATH = config['backup_path']
LIBRARIES = config['libraries']

# === End - Config and Global Variables ===

if __name__ == '__main__':
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
        print('\nLoading...')
        manager = MirrorManager(SOURCE_PATH, BACKUP_PATH, LIBRARIES)
        manager.load_mirrors()
        manager.load_mirror_libraries()
        menus.main.run(manager)
    else:
        print(
            'Python {}.{} detected'.format(sys.version_info[0], sys.version_info[1]) +
            '\nPython 3.5 or greater required'
        )
