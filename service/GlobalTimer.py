from apscheduler.schedulers.asyncio import AsyncIOScheduler
from service.Background import *

scheduler = AsyncIOScheduler()
scheduler.add_job(refresh_running, "interval", minutes=1)


async def timer():
    # 单次任务
    # 初始化正在进行的课程
    await initialize_running()
    # 更新课程完成率名单
    await update_statistic_course_finish_rate()
    # 更新总体完成率名单
    await update_statistic_member_finish_rate()

    scheduler.start()
