'''
    This class is generic exceptions, we used the class to return relent errors to user when exception is thrown during the process.
'''
class UnicornException(Exception):
    def __init__(self, name: str, details: str, status_code: int):
        self.name = name
        self.details =details
        self.status_code= status_code
