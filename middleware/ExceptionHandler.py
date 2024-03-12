from starlette.requests import Request
from starlette.responses import JSONResponse
from entity.response import normal_resp


class ValidatorError(Exception):
    def __init__(self, detail):
        super().__init__(self)
        self.detail=detail
    def __str__(self):
        return self.detail


class AuthError(Exception):
    def __init__(self, detail):
        super().__init__(self)
        self.detail=detail
    def __str__(self):
        return self.detail


async def general_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, ValidatorError):
        return JSONResponse(normal_resp.fail(422, str(exc)))
    elif isinstance(exc, AuthError):
        return JSONResponse(normal_resp.fail(401, str(exc)))
    else:
        return JSONResponse(normal_resp.fail(500, "内部错误"))
