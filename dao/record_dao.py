from tortoise import Tortoise
from config import ENVIRONMENT


async def get_courses_should_finish(mem_id):
    db = Tortoise.get_connection(ENVIRONMENT)
    return await db.execute_query_dict("SELECT course.id, type, title, start_datetime, end_datetime, cover, uri "
                                       "FROM course WHERE start_datetime >= "
                                       "(SELECT join_datetime FROM member WHERE id = %s)", [mem_id,])


async def get_courses_finished(mem_id):
    db = Tortoise.get_connection(ENVIRONMENT)
    return await db.execute_query_dict("SELECT course.id, type, title, start_datetime, end_datetime, cover, uri "
                                       "FROM course "
                                       "JOIN membercourse ON membercourse.course_id = course.id "
                                       "WHERE member_id = %s", [mem_id,])

