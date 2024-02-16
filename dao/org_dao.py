from entity.db_entity import *
from tortoise.functions import Count


async def get_orgs_members_cnt():
    await Member.all().select_related("organization__id")\
                .annotate(count=Count("id")).group_by("organization__id")\
                .values("organization__id", "organization__title", "count")