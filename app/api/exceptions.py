class RequestError(Exception):
    def __init__(self, error_code, msg, *args, **kwargs):
        self.error_code = error_code
        self.msg = msg
        super().__init__(*args, **kwargs)


class ParamError(RequestError):
    pass
