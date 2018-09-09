class Result(object):
    def __init__(self, subject: str, success: bool=False, message: str=None):
        self.subject = subject
        self.success = success
        self.message = message