import asyncio
import threading
import time

from fastapi import FastAPI
import uvicorn
from config import *
from starlette.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from contextlib import asynccontextmanager

from controller.p_org import p_org
from controller.record import record
from controller.member import member
from controller.test import test
from controller.course import course
from controller.organization import organization
from service.DataIn.InterfacePraparation import YouthBigLearning
from service.GlobalTimer import scheduler
from service.TotalCourseFinishStatistic import TotalCourseRateService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 项目启动前要做的
    scheduler.start()
    yield
    # 项目运行结束后后要做的

app = FastAPI(lifespan=lifespan)

app.include_router(test, prefix="/test", tags=["test_api"])
app.include_router(course, prefix="/course", tags=["course_api"])
app.include_router(organization, prefix="/organization", tags=["organization_api"])
app.include_router(member, prefix="/member", tags=["member_api"])
app.include_router(record, prefix="/finish_record", tags=["finish_record_api"])
app.include_router(p_org, prefix="/p_org", tags=["p_org_api"])

register_tortoise(
    app=app,
    config=TORTOISE_ORM
)


if __name__ == '__main__':
    if LOGIN_AT_STARTUP:
        youth_learning = YouthBigLearning()

    uvicorn.run("main:app", host=SERVER_IP, port=SERVER_PORT)
