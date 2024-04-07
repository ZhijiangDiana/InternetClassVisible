import xgboost as xgb
import numpy as np

from entity.db_entity import *
from tortoise import Tortoise
from config import TORTOISE_ORM

from collections import OrderedDict
from abc import ABC, abstractmethod
from typing import List, Dict, Union, Tuple
from datetime import datetime, timedelta


class probaPredModel(ABC):
    model = xgb.Booster(model_file="ai/proba_pred/model.json")
    # 上次刷新时间
    _refresh_time: datetime = None
    # 多久刷新一次
    _refresh_cycle: timedelta = timedelta(days=1)
    all_course: OrderedDict = None
    _stu_proba_cache: Dict[int, Tuple[Union[float, datetime]]] = dict()


    @abstractmethod
    def _() -> None:
        pass

    @classmethod
    async def refresh(cls) -> None:
        # if len(Tortoise.apps) == 0:
        #     print('[WARNING] 未连接数据库')
        #     await Tortoise.init(config=TORTOISE_ORM)

        if cls.all_course is None or cls._refresh_time is None or (datetime.now() - cls._refresh_time) > cls._refresh_cycle:
            cls.all_course = await Course.all().values("id", "start_datetime")
            cls.all_course = OrderedDict({c["id"]: c["start_datetime"] for c in sorted(cls.all_course, key=lambda t: t["start_datetime"])})
            cls.refresh_time = datetime.now()

    @classmethod
    def _getContinueFinish(cls, course_ids: List[int]) -> int:
        all_course = list(cls.all_course.keys())
        offset = all_course.index(course_ids[-1])
        continuous_finish_num = 0
        for i in range(1, len(course_ids) + 1):
            if course_ids[-i] == all_course[offset - i + 1]:
                continuous_finish_num += 1
            else:
                break
        return continuous_finish_num

    @classmethod
    async def proba_pred(cls, student_id: int) -> float:
        if student_id in cls._stu_proba_cache.keys() and (datetime.now() - cls._stu_proba_cache[student_id][1]) < cls._refresh_cycle:
            return cls._stu_proba_cache[student_id][0]
        
        await cls.refresh()
        stu_course = await MemberCourse.filter(member_id=student_id).values_list("course_id", "finish_datetime")
        if len(stu_course) == 0:
            proba = 0.0
        else:
            stu_course.sort(key=lambda x: x[1])
            ci, fd = map(list, zip(*stu_course))

            continuous_finish = np.array([cls._getContinueFinish(ci[:i]) for i in range(1, len(fd) + 1)])
            total_finish = np.array([len(ci[:i]) for i in range(1, len(fd) + 1)])
            interrupt_finish_cnt = np.cumsum(continuous_finish == 1)

            feature = [[continuous_finish[-1], total_finish[-1], interrupt_finish_cnt[-1]]]
            feature = xgb.DMatrix(feature)
            proba = cls.model.predict(feature)[0].tolist()
        
        cls._stu_proba_cache[student_id] = (proba, datetime.now())

        return proba
