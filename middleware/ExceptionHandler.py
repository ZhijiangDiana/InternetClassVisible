from fastapi import HTTPException
from fastapi.exception_handlers import http_exception_handler
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from entity.response import normal_resp


async def general_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, ValidationError):
        return JSONResponse(normal_resp.fail(HTTP_422_UNPROCESSABLE_ENTITY, "实体不合法"), status_code=HTTP_422_UNPROCESSABLE_ENTITY)
    elif isinstance(exc, HTTPException):
        return await http_exception_handler(request, exc)
    else:
        return JSONResponse(normal_resp.fail(500, "内部错误").__dict__(), status_code=500)
