class RequestFailed(Exception):
    """
    Raised when received 'N'.

    Received last command but there was a problem, invalid command
    was received or Status of a measurement was BAD.
    """

    pass


class UnexpectedResponse(Exception):
    """Raised when received unknown feedback"""

    pass


class ErrorOccurred(Exception):
    """
    Raised when received 'E'.

    Indicates an Error has occurred on the HOST PC that needs user
    attention. Usually this is a message box on the Host PC screen
    that needs to be “LOCALLY” acknowledged.
    """

    pass
