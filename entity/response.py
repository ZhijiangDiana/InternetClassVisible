from typing import Any, Optional


class normal_resp():
    success: bool
    status: int
    message: str
    result: dict
    debug: str

    def __init__(self, success=True, status=200, message="", result=None, debug=""):
        self.success = success
        self.status = status
        self.message = message
        self.result = result
        self.debug = debug

    def __dict__(self) -> dict:
        return {
            "success": self.success,
            "status": self.status,
            "message": self.message,
            "data": self.result,
            "debug": self.debug
        }

    @staticmethod
    def success(result):
        return normal_resp(result=result).__dict__()

    @staticmethod
    def fail(status, message):
        return normal_resp(success=False, status=status, message=message).__dict__()

