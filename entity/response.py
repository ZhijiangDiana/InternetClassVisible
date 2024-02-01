from typing import Any


class normal_resp():
    status: int
    message: str
    result: {}
    debug: str

    def __init__(self, status=200, message="", result=None, debug=""):
        self.status = status
        self.message = message
        self.result = result
        self.debug = debug

