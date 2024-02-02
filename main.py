from fastapi import FastAPI
import uvicorn
from config import *
from starlette.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from controller.record import record
from controller.member import member
from controller.test import test
from controller.course import course
from controller.organization import organization
from service.DataIn.InterfacePraparation import YouthBigLearning
from service.MemberFinishStatistic import CalculateRateService

app = FastAPI()

app.include_router(test, prefix="/test", tags=["test_api"])
app.include_router(course, prefix="/course", tags=["course_api"])
app.include_router(organization, prefix="/organization", tags=["organization_api"])
app.include_router(member, prefix="/member", tags=["member_api"])
app.include_router(record, prefix="/finish_record", tags=["finish_record_api"])

register_tortoise(
    app=app,
    config=TORTOISE_ORM
)

if __name__ == '__main__':
    # 实例化所有业务
    CalculateRateService()
    if LOGIN_AT_STARTUP:
        youth_learning = YouthBigLearning()

    uvicorn.run("main:app", host='localhost', port=8080)
