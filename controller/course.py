import json

from fastapi import APIRouter
from pydantic import BaseModel, validator

from entity.db_entity import *

course = APIRouter()


@course.post("/add_all")
async def add_all():
    with open(f"all_course.json", "r", encoding="utf-8") as all_course:
        all_course = json.load(all_course)
        for one_course in all_course["result"]["list"]:
            start_time = min(one_course["startTime"], one_course["createTime"])
            added_course = await Course.create(id=one_course["id"], type=one_course["type"], title=one_course["title"],
                                start_datetime=start_time, end_datetime=one_course["endTime"],
                                cover=one_course["cover"], uri=one_course["uri"])
            print(added_course)

    return True

