from config import ENVIRONMENT
from tortoise import Tortoise


async def get_orgs_members_cnt():
    db = Tortoise.get_connection(ENVIRONMENT)
    return await db.execute_query_dict("SELECT organization_id, title, COUNT(*) FROM member "
                                       "JOIN organization ON member.organization_id = organization.id "
                                       "GROUP BY organization_id;")

