import asyncio
from abc import ABC, abstractmethod
import datetime
from typing import Dict, List, Tuple, Union
from collections import Counter, OrderedDict

from entity.db_entity import *


class SemesterStatistic(ABC):
    # 学期: {学生id: 完成率} 按完成率排序
    _stuFinishRate: Dict[str, Union[OrderedDict[int, float], Dict[int, int]]] = dict()
    _stuFinishRateLock = asyncio.Lock()

    # 学期: {支部编号: 完成率} 按完成率排序
    _orgFinishRate: Dict[str, Union[OrderedDict[str, float], Dict[str, int]]] = dict()
    _orgFinishRateLock = asyncio.Lock()

    # 上次更新的完成记录中最晚一条的时间
    _refreshTime = datetime.datetime(2000, 1, 1)
    _refreshTimeLock = asyncio.Lock()

    # 用春节作为寒假分界线
    # 用8月中旬作为暑假分界线
    # http://interesting-sky.china-vo.org/astronomical-database/other/millennium-new-year-date-table/
    # r'>' + str(year) + r'</span>[\s\S]+?<span[\s\S]+?>([0-9]{4})</span>'
    spring_festival = {
        2001: datetime.datetime(2001, 1, 24),
        2002: datetime.datetime(2002, 2, 12),
        2003: datetime.datetime(2003, 2, 1),
        2004: datetime.datetime(2004, 1, 22),
        2005: datetime.datetime(2005, 2, 9),
        2006: datetime.datetime(2006, 1, 29),
        2007: datetime.datetime(2007, 2, 18),
        2008: datetime.datetime(2008, 2, 7),
        2009: datetime.datetime(2009, 1, 26),
        2010: datetime.datetime(2010, 2, 14),
        2011: datetime.datetime(2011, 2, 3),
        2012: datetime.datetime(2012, 1, 23),
        2013: datetime.datetime(2013, 2, 10),
        2014: datetime.datetime(2014, 1, 31),
        2015: datetime.datetime(2015, 2, 19),
        2016: datetime.datetime(2016, 2, 8),
        2017: datetime.datetime(2017, 1, 28),
        2018: datetime.datetime(2018, 2, 16),
        2019: datetime.datetime(2019, 2, 5),
        2020: datetime.datetime(2020, 1, 25),
        2021: datetime.datetime(2021, 2, 12),
        2022: datetime.datetime(2022, 2, 1),
        2023: datetime.datetime(2023, 1, 22),
        2024: datetime.datetime(2024, 2, 10),
        2025: datetime.datetime(2025, 1, 29),
        2026: datetime.datetime(2026, 2, 17),
        2027: datetime.datetime(2027, 2, 6),
        2028: datetime.datetime(2028, 1, 26),
        2029: datetime.datetime(2029, 2, 13),
        2030: datetime.datetime(2030, 2, 3),
        2031: datetime.datetime(2031, 1, 23),
        2032: datetime.datetime(2032, 2, 11),
        2033: datetime.datetime(2033, 1, 31),
        2034: datetime.datetime(2034, 2, 19),
        2035: datetime.datetime(2035, 2, 8),
        2036: datetime.datetime(2036, 1, 28),
        2037: datetime.datetime(2037, 2, 15),
        2038: datetime.datetime(2038, 2, 4),
        2039: datetime.datetime(2039, 1, 24),
        2040: datetime.datetime(2040, 2, 12),
        2041: datetime.datetime(2041, 2, 1),
        2042: datetime.datetime(2042, 1, 22),
        2043: datetime.datetime(2043, 2, 10),
        2044: datetime.datetime(2044, 1, 30),
        2045: datetime.datetime(2045, 2, 17),
        2046: datetime.datetime(2046, 2, 6),
        2047: datetime.datetime(2047, 1, 26),
        2048: datetime.datetime(2048, 2, 14),
        2049: datetime.datetime(2049, 2, 2),
        2050: datetime.datetime(2050, 1, 23)
    }

    # 阻止实例化
    @abstractmethod
    def _() -> None:
        pass

    @classmethod
    def _date2semester(cls, date: datetime.datetime) -> str:
        date = date.replace(tzinfo=None)
        year = date.year
        if date < cls.spring_festival[year]:
            return f"{year - 1}-{year}学年第一学期"
        elif date < datetime.datetime(year, 8, 15):
            return f"{year - 1}-{year}学年第二学期"
        else:
            return f"{year}-{year + 1}学年第一学期"
    
    @classmethod
    def _semester2date(cls, semester: str) -> Tuple[datetime.datetime]:
        year = int(semester.split("-")[0])
        if semester.endswith("第一学期"):
            return datetime.datetime(year, 8, 15), cls.spring_festival[year+1]
        elif semester.endswith("第二学期"):
            return cls.spring_festival[year+1], datetime.datetime(year+1, 8, 15)
        else:
            raise ValueError("学期格式错误")

    # 初始化完成率
    @classmethod
    async def initSemesterStatistic(cls) -> None:
        print("初始化学期数据")
        # 初始化过程_refreshTime不用作数据库查询, 只用于指示最近的学期
        async with cls._refreshTimeLock:
            cls._refreshTime = max(await MemberCourse.all().values_list("finish_datetime"))[0]
        async with cls._stuFinishRateLock:
            cls._stuFinishRate = await cls._initStuFinishRate()
        async with cls._orgFinishRateLock:
            cls._orgFinishRate = await cls._initOrgFinishRate()
        print("学期数据初始化完成")

    # 初始化所有学期的学生完成率
    @classmethod
    async def _initStuFinishRate(cls) -> Dict[str, Union[OrderedDict[int, float], Dict[int, int]]]:
        all_sem = Counter(map(lambda x: cls._date2semester(x[0]), (await Course.all().values_list("start_datetime"))))
        current_sem = cls._date2semester(cls._refreshTime)

        # 初始化为全0
        stuFinishRate = {sem:{i[0]: 0 for i in (await Member.filter(join_datetime__lte=datetime.datetime(int(sem[:4]), 9, 1)).values_list("id"))} 
                         for sem in all_sem.keys()}

        stu_stat = await MemberCourse.all().prefetch_related("course").values_list("course__start_datetime", "member_id")
        for course_time, stu_id in stu_stat:
            sem = cls._date2semester(course_time)
            stuFinishRate[sem][stu_id] += 1

        stuFinishRate = {
            sem: OrderedDict(sorted([[k, v / all_sem[sem]] for k, v in stuFinishRate[sem].items()], key=lambda x: x[1], reverse=True))
            if sem != current_sem else stuFinishRate[sem]
            for sem in stuFinishRate.keys() 
        }

        return stuFinishRate

    # 初始化所有学期的支部完成率
    @classmethod
    async def _initOrgFinishRate(cls) -> Dict[str, Union[OrderedDict[int, float], Dict[int, int]]]:
        orgFinishRate = {sem:dict() for sem in cls._stuFinishRate.keys()}
        current_sem = cls._date2semester(cls._refreshTime)

        for sem in orgFinishRate.keys():
            mem2org = await Member.filter(join_datetime__lte=datetime.datetime(int(sem[:4]), 9, 1)).values_list("id", "organization_id")
            mem2org = {i[0]: i[1] for i in mem2org}
            orgFinishRate[sem] = {org: 0 for org in set(mem2org.values())}
            org2memberNum = Counter(mem2org.values())

            # 往期为rate 当期为count
            for member_id, rate_or_count in cls._stuFinishRate[sem].items():
                orgFinishRate[sem][mem2org[member_id]] += rate_or_count

            if sem != current_sem:
                orgFinishRate[sem] = OrderedDict(sorted([[org, orgFinishRate[sem][org] / org2memberNum[org]] for org in orgFinishRate[sem].keys()], key=lambda x: x[1], reverse=True))
        
        return orgFinishRate

    # 定时每周运行以更新学期统计数据
    @classmethod
    async def updateweekStatistic(cls) -> None:
        finish_datetimes = [i[0] for i in (await MemberCourse.filter(finish_datetime__gt=cls._refreshTime).values_list("finish_datetime"))]
        current_sem = list(set(map(cls._date2semester, finish_datetimes)))
        
        if len(current_sem) == 0:
            return
        assert len(current_sem) == 1, \
            "未更新的课程列表跨学期, 可能的原因是过长时间没有更新课程或没有初始化, 手动重启项目以初始化学期数据"
        current_sem = current_sem[0]

        if len(finish_datetimes) > 0:
            async with cls._stuFinishRateLock:
                cls._stuFinishRate[current_sem] = await cls._updateStuFinishCount(current_sem)
            async with cls._orgFinishRateLock:
                cls._orgFinishRate[current_sem] = await cls._updateOrgFinishCount(current_sem)
            async with cls._refreshTimeLock:
                cls._refreshTime = max(finish_datetimes)
        else:
            print(f"[WARNING] {datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day} " + 
                  "SemesterStatistic.updateweekStatistic 没有新的数据可供更新")

    # 每周更新当前学期的个人数据
    @classmethod
    async def _updateStuFinishCount(cls, current_sem:str) -> Dict[int, int]:
        stu_stat = await MemberCourse.filter(finish_datetime__gt=cls._refreshTime).values_list("member_id")
        if current_sem not in cls._stuFinishRate.keys():
            if len(set([type(v) for k, v in cls._stuFinishRate.items()])) != 1:
                await cls.updateSemesterFinishRate()
            currentSemStuFinishCount = {i[0]: 0 for i in (await Member.filter(join_datetime__lte=datetime.datetime(int(current_sem[:4]), 9, 1)).values_list("id"))}
        else:
            currentSemStuFinishCount = cls._stuFinishRate[current_sem]

        for stu_id in stu_stat:
            currentSemStuFinishCount[stu_id[0]] += 1
        return currentSemStuFinishCount

    # 每周更新当前学期的支部数据
    @classmethod
    async def _updateOrgFinishCount(cls, current_sem:str) -> Dict[str, int]:
        if current_sem not in cls._orgFinishRate.keys():
            currentSemOrgFinishCount = {i[0]: 0 for i in (await Organization.filter(create_time__gt=datetime.datetime(int(current_sem[:4]), 9, 1)).values_list("id"))}
        else:
            tmp = cls._orgFinishRate[current_sem]
            currentSemOrgFinishCount = tmp if type(tmp) is dict else {i[0]:i[1] for i in tmp}
        mem2org = await Member.filter(join_datetime__lte=datetime.datetime(int(current_sem[:4]), 9, 1)).values_list("id", "organization_id")
        mem2org = {i[0]: i[1] for i in mem2org}
        assert type(cls._stuFinishRate[current_sem]) is dict, \
            "type(cls._stuFinishRate[current_sem]) 应为dict, 可能的原因是单独调用了此方法, 使得SemesterStatistic._updateStuFinishCount未执行"
        for member_id, count in cls._stuFinishRate[current_sem].items():
            currentSemOrgFinishCount[mem2org[member_id]] += count
        return currentSemOrgFinishCount

    # 学期末计算完成率并排序
    @classmethod
    async def updateSemesterFinishRate(cls) -> None:
        for k, v in cls._stuFinishRate.items():
            if type(v) is dict:
                current_sem = k
                break
        for k, v in cls._orgFinishRate.items():
            if type(v) is dict:
                assert current_sem == k
                break
        
        sem_start_date, sem_end_date = cls._semester2date(current_sem)
        course_num = len(await Course.filter(start_datetime__gt=sem_start_date, start_datetime__lt=sem_end_date).values_list("id"))

        currentSemStuFinishCount: Dict[int, int] = cls._stuFinishRate[current_sem]
        async with cls._stuFinishRateLock:
            cls._stuFinishRate[current_sem] = OrderedDict(sorted([[stu_id, count/course_num] for stu_id, count in currentSemStuFinishCount.items()], key=lambda x: x[1], reverse=True))

        currentSemOrgFinishCount: Dict[str, int] = cls._orgFinishRate[current_sem]
        org2stuNum = await Member.filter(join_datetime__lte=datetime.datetime(int(current_sem[:4]), 9, 1)).values_list("organization_id")
        org2stuNum = Counter([org[0] for org in org2stuNum])
        async with cls._orgFinishRateLock:
            cls._orgFinishRate[current_sem] = OrderedDict(sorted([[org_id, count/(course_num*org2stuNum[org_id])] for org_id, count in currentSemOrgFinishCount.items()], key=lambda x: x[1], reverse=True))

    # 某学期全部学生的完成率排名
    @classmethod
    async def get_all_stu_rank(cls, semester: str) -> Dict[int, float]:
        return dict(cls._stuFinishRate[semester])
    
    # 某学期某学生的完成率和名次
    @classmethod
    async def get_stu_rank(cls, semester: str, stu_id: int) -> Tuple[Union[float, int]]:
        rate = cls._stuFinishRate[semester][stu_id]
        rank = list(cls._stuFinishRate[semester].keys()).index(stu_id) + 1
        return rate, rank
    
    # 某学期全部支部的完成率排名
    # {"name":str, "value":float}
    @classmethod
    async def get_all_org_rank(cls, semester: str) -> Dict[str, float]:
        return dict(cls._orgFinishRate[semester])
    
    # 某学期某支部的完成率和名次
    @classmethod
    async def get_org_rank(cls, semester: str, org_id: str) -> Tuple[Union[float, int]]:
        rate = cls._orgFinishRate[semester][org_id]
        rank = list(cls._orgFinishRate[semester].keys()).index(org_id) + 1
        return rate, rank
    
    # 某学期某支部学生的排名
    @classmethod
    async def get_org_stu_rank(cls, semester: str, org_id: str) -> Dict[int, float]:
        stu4org = [i[0] for i in await Member.filter(organization_id=org_id).values_list("id")]
        org_stu_rank = {s[0]: s[1] for s in cls._stuFinishRate[semester].items() if s[0] in stu4org}
        return org_stu_rank
