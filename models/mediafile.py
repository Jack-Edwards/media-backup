import datetime
import hashlib
import os

class MediaFile(object):
    def __init__(self, path, path_in_library, source):
        self.name= os.path.basename(path)
        self.ext = os.path.splitext(self.name)[1]
        self.source= source
        self.path = path
        self.path_in_library = path_in_library
        self.cache_file = os.path.join(
                os.path.dirname(self.path),
                '.cache',
                '{}.txt'.format(self.name)
            )

        self._real_hash = None
        self._cached_hash = None
        self._cached_date = None

    @property
    def real_hash(self):
        if self._real_hash is None:
            self.generate_hash()
            return self._real_hash
        else:
            return self._real_hash

    @real_hash.setter
    def real_hash(self, value):
        self._real_hash = value

    @property
    def cached_hash(self):
        if self._cached_hash is None:
            self.load_hash_from_file()
            return self._cached_hash
        else:
            return self._cached_hash

    @cached_hash.setter
    def cached_hash(self, value):
        self._cached_hash = value

    @property
    def cached_date(self):
        if self._cached_date is None:
            self.load_hash_from_file()
            return self._cached_date
        else:
            return self._cached_date

    @cached_date.setter
    def cached_date(self, value):
        self._cached_date = value

    @property
    def cache_is_stale(self):
        three_months_ago = datetime.date.today() - datetime.timedelta(days=90)
        cached_date = datetime.datetime.strptime(self.cached_date, '%Y-%m-%d').date()
        if cached_date < three_months_ago:
            return True
        else:
            return False

    #  Generate a new hash and store as self._real_hash
    def generate_hash(self):
        sha1 = hashlib.sha1()
        with open(self.path, 'rb') as file:
            while True:
                data = file.read(65536)
                if not data:
                    break
                sha1.update(data)
            self.real_hash = sha1.hexdigest()

    #  Save the generated hash to cache file
    def save_hash_to_file(self, overwrite):
        #  Careful not to overwrite an existing cache file without explicit permission to do so
        if overwrite or not os.path.exists(self.cache_file):
            today = str(datetime.date.today())
            self.cached_date = today

            #  Create missing directories
            if not os.path.exists(os.path.dirname(self.cache_file)):
                os.mkdir(os.path.dirname(self.cache_file))

            #  Open the file in "write" mode
            #  An existing file with the same name will be replaced
            with open(self.cache_file, 'w') as file:
                line = '{}|{}'.format(today, self.real_hash)
                file.write(line)

    def load_hash_from_file(self):
        #  Hash file exists; proceed with loading hash from file
        if os.path.isfile(self.cache_file):
            with open(self.cache_file, 'r') as file:
                line = file.readline()
                if '|' in line:
                    split = line.split('|')
                    if len(split) == 2:
                        self.cached_date = line.split('|')[0].strip()
                        self.cached_hash = line.split('|')[1].strip()
                    else:
                        raise SyntaxError('Unexpected number of items in cache file')
                else:
                    raise SyntaxError('Unexpected cache file format')

        #  Hash file does not exist; make a new one
        else:
            self.save_hash_to_file(False)
            self.load_hash_from_file()