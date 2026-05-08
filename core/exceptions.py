from typing import Optional


class ApiException(Exception):
    def __init__(self, statusCode: int, message: str, responseBody: Optional[str] = None):
        super().__init__(message)
        self.statusCode = statusCode
        self.responseBody = responseBody