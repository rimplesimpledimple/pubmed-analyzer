class UserFacingError(Exception):
    """Base exception class for errors that can be safely shown to users."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InternalError(Exception):
    """Base exception class for internal system errors that should not be exposed to users."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
