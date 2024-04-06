from entity.db_entity import *
from datetime import *


class DailyRecordService:
    # 过去一年每天的完成情况
    daily_status = None

    @classmethod
    async def get_daily_status(cls):
        if cls.daily_status is None:
            print("正在计算每日完成数")
            cls.daily_status = []
            current_date = datetime.now()
            begin = current_date.replace(year=current_date.year - 1, month=1, day=1)
            end = current_date.replace(year=current_date.year, month=1, day=1)

            current_day = begin
            while current_day < end:
                current_day_begin = current_day.replace(hour=0, minute=0, second=0)
                current_day_end = current_day.replace(hour=23, minute=59, second=59)
                item = [current_day_begin.strftime("%Y-%m-%d"), await MemberCourse.filter(finish_datetime__gte=current_day_begin,
                                                               finish_datetime__lte=current_day_end).count()]
                cls.daily_status.append(item)

                current_day += timedelta(days=1)

        return cls.daily_status
