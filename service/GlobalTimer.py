from apscheduler.schedulers.asyncio import AsyncIOScheduler
from service.Background import *
from service.DailyRecordService import DailyRecordService
from service.SemesterStatistic import SemesterStatistic
from controller.auth import AuthHandler
from tortoise import Tortoise
from config import TORTOISE_ORM
import datetime


scheduler = AsyncIOScheduler()


async def initialize():
    await Tortoise.init(config=TORTOISE_ORM)

    # 单次任务
    # 初始化正在进行的课程
    await initialize_running()
    # 更新课程完成率名单
    await update_statistic_course_finish_rate()
    # 更新总体完成率名单
    await update_statistic_member_finish_rate()
    # 更新每日完成名单
    await DailyRecordService.get_daily_status()
    # 初始化学期数据
    await SemesterStatistic.initSemesterStatistic()
    # 检查数据库中是否有明文密码并加密
    await AuthHandler.init_base_password()

    await Tortoise.close_connections()
    print("\033[32m初始化完成\033[0m")

    # 初始化结束后开始定时更新
    # scheduler.add_job(refresh_running, "interval", minutes=1, args=[])


scheduler.add_job(initialize, "date", next_run_time=datetime.datetime.now() + datetime.timedelta(seconds=2), args=[])
