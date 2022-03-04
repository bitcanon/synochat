# define Python user-defined exceptions
class Error(Exception):
    """ Base class for other exceptions """
    pass


class InvalidTokenError(Error):
    """ Raised when token authentication fails. """
    
    def __init__(self, message="Authentication failed due to use of an invalid token."):
        self.message = message
        super().__init__(self.message)


class InvalidApiError(Error):
    """ Raised when an invalid API is used. """
    
    def __init__(self, message="Request failed due to use of an invalid API identifier."):
        self.message = message
        super().__init__(self.message)


class InvalidMethodError(Error):
    """ Raised when an invalid method is used. """
    
    def __init__(self, message="Request failed due to use of an unsupported method."):
        self.message = message
        super().__init__(self.message)


class InvalidVersionError(Error):
    """ Raised when an invalid version is used. """
    
    def __init__(self, message="Request failed due to use of an unsupported version."):
        self.message = message
        super().__init__(self.message)


class InvalidPayloadError(Error):
    """ Raised when an invalid payload is used. """
    
    def __init__(self, message="Request failed due to use of an invalid message payload."):
        self.message = message
        super().__init__(self.message)


class UnknownApiError(Error):
    """
    Raised when an unknown error occurs.
    These are undocumented response values from the Synology Chat API.
    """
    
    def __init__(self, message="Undefined"):
        self.message = f"Unknown API error occured: {message}"
        super().__init__(self.message)

