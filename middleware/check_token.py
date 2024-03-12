from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.datastructures import MutableHeaders
from entity.response import normal_resp
from controller import auth


class CheckToken(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        authorization_header = request.headers.get("authorization")
        if not authorization_header:
            new_header = MutableHeaders(request.headers)
            new_header["authorization"] = "Bearer default"
            request.scope.update(headers=new_header.raw)
        # 过滤特定接口, 以完成登录, 开发时不能用, 会导致/docs无法访问
        # if request.url.components[2] not in (list(map(lambda x: "/authentication"+ x.path, auth.routes))):
        #     return JSONResponse(content=normal_resp.fail(302, "缺少token"))
        response = await call_next(request)
        return response