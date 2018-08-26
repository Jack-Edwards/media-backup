import datetime
import hashlib
import os

class MediaFile(object):
    def __init__(self, path, path_in_library, source):
        self.name = os.path.basename(path)
        self.ext = os.path.splitext(self.name)[1]
        self.source = source
        self.path = path
        self.path_in_library = path_in_library
        self.cache_file = os.path.join(
            os.path.dirname(self.path),
            '.cache',
            '{}.txt'.format(self.name)
        )

        self._real_checksum = None
        self._cached_checksum = None
        self._cached_date = None

    @property
    def real_checksum(self):
        if self._real_checksum is None:
            self.generate_checksum()
            return self._real_checksum
        else:
            return self._real_checksum

    @real_checksum.setter
    def real_checksum(self, value):
        self._real_checksum = value

    @property
    def real_checksum_has_been_set(self):
        if self._real_checksum is not None:
            return True

    @property
    def cached_checksum(self):
        if self._cached_checksum is None:
            self.load_checksum_from_cache()
            return self._cached_checksum
        else:
            return self._cached_checksum

    @cached_checksum.setter
    def cached_checksum(self, value):
        self._cached_checksum = value

    @property
    def cached_date(self):
        if self._cached_date is None:
            self.load_checksum_from_cache()
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

    @property
    def real_and_cached_checksums_match(self):
        if self.real_checksum == self.cached_checksum:
            return True
        else:
            return False

    #  Generate a new checksum and store as self._real_checksum
    def generate_checksum(self):
        sha1 = hashlib.sha1()
        with open(self.path, 'rb') as file:
            while True:
                data = file.read(65536)
                if not data:
                    break
                sha1.update(data)
            self.real_checksum = sha1.hexdigest()

    #  Save the generated checksum to cache file
    def save_checksum_to_cache(self, overwrite):
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
                line = '{}|{}'.format(today, self.real_checksum)
                file.write(line)

    def load_checksum_from_cache(self):
        if os.path.isfile(self.cache_file):
            with open(self.cache_file, 'r') as file:
                line = file.readline()
                if '|' in line:
                    split = line.split('|')
                    if len(split) == 2:
                        self.cached_date = line.split('|')[0].strip()
                        self.cached_checksum = line.split('|')[1].strip()
                    else:
                        raise SyntaxError('Unexpected number of items in cache file')
                else:
                    raise SyntaxError('Unexpected cache file format')

        #  Cache file does not exist; make a new one
        else:
            self.save_checksum_to_cache(False)
            self.load_checksum_from_cache()

    def refresh_cache(self):
        if self.real_and_cached_checksums_match:
            self.save_checksum_to_cache(True)
        else:
            raise ValueError('Real and checksums do not match')