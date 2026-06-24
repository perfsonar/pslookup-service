from .message import Message

class RegisterRequest(Message):

    def __init__(self, message=None):
        if not message:
            message = {}
        super().__init__(message)
        