from apscheduler.schedulers.asyncio import AsyncIOScheduler
from service.Background import *
from service.SemesterStatistic import SemesterStatistic
from tortoise import Tortoise
from config import TORTOISE_ORM
import datetime


async def initialize():
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 单次任务
    # 初始化正在进行的课程
    await initialize_running()
    # 更新课程完成率名单
    await update_statistic_course_finish_rate()
    # 更新总体完成率名单
    await update_statistic_member_finish_rate()

    # 初始化学期数据
    await SemesterStatistic.initSemesterStatistic()

    await Tortoise.close_connections()


scheduler = AsyncIOScheduler()
scheduler.add_job(initialize, "date", next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=2), args=[])
scheduler.add_job(refresh_running, "interval", minutes=1, args=[])