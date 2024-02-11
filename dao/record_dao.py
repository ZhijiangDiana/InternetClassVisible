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


async def get_org_records(org_id, course_id):
    db = Tortoise.get_connection(ENVIRONMENT)
    return await db.execute_query_dict("SELECT * FROM membercourse WHERE member_id in "
                                       "(SELECT id FROM member WHERE organization_id = %s)"
                                       "AND course_id = %s", [org_id, course_id,])



