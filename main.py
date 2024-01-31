from fastapi import FastAPI
import uvicorn
from config import TORTOISE_ORM
from starlette.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from controller.test import test
from controller.course import course
from controller.organization import organization

app = FastAPI()

app.include_router(test, prefix="/test", tags=["test_api"])
app.include_router(course, prefix="/course", tags=["course_api"])
app.include_router(organization, prefix="/organization", tags=["course_api"])

register_tortoise(
    app=app,
    config=TORTOISE_ORM
)

if __name__ == '__main__':
    uvicorn.run("main:app", host='localhost', port=8080)
