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
        self._real_mtime = None
        self._real_size = None
        self._cached_checksum = None
        self._cached_date = None
        self._cached_mtime = None
        self._cached_size = None

    def print_info(self):
        print(
            ' > File type: {}'.format('Source' if self.source else 'Backup') +
            '\n > File modified: {}'.format(self.real_mtime) +
            '\n > File size: {}'.format(self.real_size) +
            '\n > Checksum: {}'.format(self.real_checksum) +
            '\n > Cached information:' +
            '\n >   Cache date: {}'.format(self.cached_date) +
            '\n >   File modified: {}'.format(self.cached_mtime) +
            '\n >   File size: {}'.format(self.cached_size) +
            '\n >   Checksum: {}'.format(self.cached_checksum)
        )

    @property
    def real_checksum(self):
        if self._real_checksum is None:
            self.generate_checksum()
        return self._real_checksum

    @real_checksum.setter
    def real_checksum(self, value):
        self._real_checksum = value

    @property
    def real_mtime(self):
        if self._real_mtime is None:
            self.get_mtime()
        return self._real_mtime

    @real_mtime.setter
    def real_mtime(self, value):
        self._real_mtime = value

    @property
    def real_size(self):
        if self._real_size is None:
            self.get_size()
        return self._real_size

    @real_size.setter
    def real_size(self, value):
        self._real_size = value

    @property
    def cached_checksum(self):
        if self._cached_checksum is None:
            self.load_cache_file()
        return self._cached_checksum

    @cached_checksum.setter
    def cached_checksum(self, value):
        self._cached_checksum = value

    @property
    def cached_date(self):
        if self._cached_date is None:
            self.load_cache_file()
        return self._cached_date

    @cached_date.setter
    def cached_date(self, value):
        self._cached_date = value

    @property
    def cached_mtime(self):
        if self._cached_mtime is None:
            self.load_cache_file()
        return self._cached_mtime

    @cached_mtime.setter
    def cached_mtime(self, value):
        self._cached_mtime = value

    #  Determine whether the cache file is stale, given a number of "stale_cache_days"
    def cache_is_stale(self, stale_cache_days):
        expiration_date = datetime.date.today() - datetime.timedelta(days=stale_cache_days)
        cached_date = datetime.datetime.strptime(self.cached_date, '%Y-%m-%d').date()
        return cached_date < expiration_date

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

    #  Save the cache file
    def save_cache_file(self, overwrite):
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
                line = '{0}|{1}|{2}|{3}'.format(today, self.real_checksum, self.real_mtime, self.real_size)
                file.write(line)

    #  Load the values from the cache file into the MediaFile object
    def load_cache_file(self):
        if os.path.isfile(self.cache_file):
            with open(self.cache_file, 'r') as file:
                line = file.readline()
                assert '|' in line, 'Malformed cached file: {}'.format(self.cache_file)
                split = line.split('|')
                assert len(split) >= 2, 'Too few items in cache file'
                assert len(split) <= 4, 'Too many items in cache file'
                if len(split) >= 2:
                    self.cached_date = line.split('|')[0].strip()
                    self.cached_checksum = line.split('|')[1].strip()
                if len(split) == 4:
                    self.cached_mtime = line.split('|')[2].strip()
                    self.cached_size = line.split('|')[3].strip()
        else:
            self.save_cache_file(overwrite=False)
            self.load_cache_file()

    def refresh_cache_file(self):
        assert self.real_checksum == self.cached_checksum, 'Real and cached checksums do not match'
        self.save_cache_file(overwrite=True)

    def get_mtime(self):
        self.real_mtime = str(datetime.datetime.fromtimestamp(os.path.getmtime(self.path)))

    def get_size(self):
        size_bytes = os.path.getsize(self.path)
        for string in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                self.real_size = '%4.3f %s' % (size_bytes, string)
                break
            size_bytes /= 1024.0
