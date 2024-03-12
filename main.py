from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import *
from tortoise.contrib.fastapi import register_tortoise
from contextlib import asynccontextmanager

from controller import *
from middleware import *
from service.DataIn.InterfacePraparation import YouthBigLearning
from service.GlobalTimer import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 项目启动前要做的
    scheduler.start()
    yield
    # 项目运行结束后后要做的

app = FastAPI(lifespan=lifespan)

app.add_middleware(CheckToken)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # *：代表所有客户端
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(auth, prefix="/authentication", tags=["authentication_api"])
app.include_router(course, prefix="/course", tags=["course_api"])
app.include_router(organization, prefix="/organization", tags=["organization_api"])
app.include_router(member, prefix="/member", tags=["member_api"])
app.include_router(record, prefix="/finish_record", tags=["finish_record_api"])
app.include_router(p_org, prefix="/p_org", tags=["p_org_api"])
app.include_router(semester, prefix="/semester", tags=["semester_api"])

register_tortoise(
    app=app,
    config=TORTOISE_ORM
)


if __name__ == '__main__':
    if LOGIN_AT_STARTUP:
        youth_learning = YouthBigLearning()

    uvicorn.run("main:app", host=SERVER_IP, port=SERVER_PORT, reload=True)
