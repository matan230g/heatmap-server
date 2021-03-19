
class UnicornException(Exception):
    def __init__(self, name: str, details: str, status_code: int):
        self.name = name
        self.details =details
        self.status_code= status_code
