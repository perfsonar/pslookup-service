from .message import Message

class RegisterRequest(Message):

    def __init__(self, message={}):
        super().__init__(message)
        