from .register_request import RegisterRequest

class JsonRegisterRequest(RegisterRequest):

    def __init__(self, message={}):
        super().__init__(message)