#!/usr/bin/env python3
import datetime
import inspect
import json
import os
import sys


class Logger:
    def __init__(self):
        self.reload_config()

    def reload_config(self):
        self.path = os.path.dirname(__file__)
        self.config_path = os.path.join(self.path, 'config.json')
        self.config = json.load(open(self.config_path))

    @property
    def log_file_path(self):
        return os.path.join(
            self.config['log_file']['directory'],
            '{}{}'.format(
                self.config['log_file']['name'],
                self.config['log_file']['extension']
            )
        )

    @property
    def exc_file_path(self):
        return os.path.join(
            self.config['exception_file']['directory'],
            '{}{}'.format(
                self.config['exception_file']['name'],
                self.config['exception_file']['extension']
            )
        )

    def log(self, level=5, message=None, exception=None):
        if level == 4 and not self.config['write_debug']:
            return True

        if level == 5 and not self.config['write_trace']:
            return True

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level_string = {
            0: 'SECURITY',
            1: 'FATAL',
            2: 'ERROR',
            3: 'INFO',
            4: 'DEBUG',
            5: 'TRACE'
        }
        if level not in level_string:
            level_string[level] = 'INVALID'

        if message:
            try:
                stack = inspect.stack()[1]
                with open(self.log_file_path, 'a') as f:
                    s = '{} | {} | {} | {} | {}\n'.format(now, level_string[level], stack.filename, stack.function, message)
                    f.write(s)
            except Exception:  # Don't have a reason to handle different exceptions differently right now
                print('Unhandled exception occurred: {}'.format(sys.exc_info()))

        if exception:
            try:
                stack = inspect.stack()[1]
                with open(self.exc_file_path, 'a') as f:
                    s = '{} | {} | {} | {} | {}\n'.format(now, level_string[level], stack.filename, stack.function, exception)
                    f.write(s)
            except Exception:  # Don't have a reason to handle different exceptions differently right now
                print('Unhandled exception occurred: {}'.format(sys.exc_info()))

        return True

    def security(self, message: str, exception: str):
        self.log(level=0, message=message, exception=exception)

    def fatal(self, message:str, exception: str):
        self.log(level=1, message=message, exception=exception)

    def error(self, message: str, exception: str):
        self.log(level=2, message=message, exception=exception)

    def info(self, message: str):
        self.log(level=3, message=message)

    def debug(self, message: str):
        self.log(level=4, message=message)

    def trace(self, message: str):
        self.log(level=5, message=message)

log = Logger()