import re

from pydantic import BaseModel
from pydantic.v1 import validator
from middleware.ExceptionHandler import ValidatorError

from entity.db_entity import *

# validator函数前必须有await,否则会报错
# validator函数前必须有await,否则会报错
# validator函数前必须有await,否则会报错
# validator函数前必须有await,否则会报错
# validator函数前必须有await,否则会报错

async def OrgValidator(org_id):
    if not (await Organization.exists(id=org_id)):
        raise ValidatorError("支部id不存在")
    return org_id


async def MemberValidator(mem_id):
    if not (await Member.exists(id=mem_id)):
        raise ValidatorError("成员id不存在")
    return mem_id


async def CourseValidator(course_id):
    if not (await Course.exists(id=course_id)):
        raise ValidatorError("课程id不存在")
    return course_id


async def EmailValidator(email):
    if not re.match(r"\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}", email):
        raise ValidatorError("输入邮箱不合法")
    return email


class AuthUser(BaseModel):
    username: str
    password: str

    @validator("password")
    def validate_password(cls, password):
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$", password):
            raise ValueError("密码必须包含大小写字母和数字, 长度大于8位")
        return password