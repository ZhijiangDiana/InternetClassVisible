import re
from typing import Union

from pydantic import BaseModel, validator
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
    # 只含姓名
    if re.match(r"^[\u4e00-\u9fa5]+(·[\u4e00-\u9fa5]+)?$", mem_id) is not None:
        if not (await Member.exists(name=mem_id)):
            raise ValidatorError("成员姓名不存在")
        return int((await Member.get(name=mem_id).values_list("id"))[0])
    # 只含数字
    elif re.match(r"^\d+$", mem_id) is not None:
        if not (await Member.exists(id=mem_id)):
            raise ValidatorError("成员id不存在")
        return int(mem_id)
    else:
        raise ValidatorError("输入成员id或姓名不合法")


async def CourseValidator(course_id):
    if not (await Course.exists(id=course_id)):
        raise ValidatorError("课程id不存在")
    return course_id


async def EmailValidator(email):
    if not re.match(r"\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}", email):
        raise ValidatorError("输入邮箱不合法")
    return email


class Password(BaseModel):
    password: str

    # @validator("password")
    # def validate_password(cls, password):
    #     if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$", password):
    #         raise ValueError("密码必须包含大小写字母和数字, 长度大于8位")
    #     return password


class AuthUser(BaseModel):
    username: Union[int, str]
    password: str