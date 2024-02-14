from pydantic import BaseModel

from entity.db_entity import *


class MemberOut():
    member: Member
    organization: Organization

    def __init__(self, member: Member, organization: Organization):
        self.member = member
        self.organization = organization

