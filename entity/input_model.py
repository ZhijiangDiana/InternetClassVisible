import re

from pydantic import BaseModel, validator

from entity.db_entity import *


class OrgValidator(BaseModel):
    org_id: str

    @validator("org_id")
    def validate_org_id(self, id_to_vali):
        if not Organization.exists(id=id_to_vali):
            raise ValueError("支部id不存在")


class MemberValidator(BaseModel):
    mem_id: int

    @validator("mem_id")
    def validate_mem_id(self, mem_id):
        if not Member.exists(id=mem_id):
            raise ValueError("成员id不存在")


class CourseValidator(BaseModel):
    course_id: str

    @validator("course_id")
    def validate_course_id(self, course_id):
        if not Course.exists(id=course_id):
            raise ValueError("课程id不存在")


class EmailValidator(BaseModel):
    email: str

    @validator("email")
    def validate_email(self, email):
        if not re.match("\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}", email):
            raise ValueError("输入邮箱不合法")

