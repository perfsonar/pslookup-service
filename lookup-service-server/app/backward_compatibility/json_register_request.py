from .register_request import RegisterRequest

class JsonRegisterRequest(RegisterRequest):

    def __init__(self, message=None):
        if not message:
            message = {}
        super().__init__(message)