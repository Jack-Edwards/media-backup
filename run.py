import os
import sys

minimum_python_version = sys.version_info[0] >= 3 and sys.version_info[1] >= 5
assert minimum_python_version, 'Python 3.5 or greater is required'

from .views import UI

if __name__ == '__main__':
    #  Find config file
    module_path = os.path.dirname(__file__)
    config_path = os.path.join(module_path, 'config.json')
    assert os.path.exists(config_path), 'Missing config file: {}'.format(config_path)

    #  Load UI
    ui = UI(config_path)
    ui.main_menu()
