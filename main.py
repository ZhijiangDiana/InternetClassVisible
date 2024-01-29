from fastapi import FastAPI
import uvicorn
from config import TORTOISE_ORM
from starlette.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise


app = FastAPI()

# register_tortoise(
#     app=app,
#     config=TORTOISE_ORM
# )

if __name__ == '__main__':
    uvicorn.run("main:app", host='localhost', port=8080)