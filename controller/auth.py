# pip install pyjwt
# pip install passlib[bcrypt]
# pip install bcrypt==4.0.1

import jwt
from fastapi import Depends, Security, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from tortoise.exceptions import MultipleObjectsReturned
from passlib.context import CryptContext
from datetime import datetime, timedelta
from entity.input_model import AuthUser, MemberValidator, Password
from entity.response import normal_resp
from entity.db_entity import Member
from middleware.ExceptionHandler import AuthError
from config import BASE_PASSWORD


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = 'SECRET'

    @classmethod
    async def init_base_password(cls):
        await Member.filter(password=BASE_PASSWORD).update(password=cls.get_password_hash(BASE_PASSWORD))

    @classmethod
    def get_password_hash(cls, password):
        return cls.pwd_context.hash(password)
    
    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return cls.pwd_context.verify(plain_password, hashed_password)
    
    @classmethod
    def encode_token(cls, member_id):
        if type(member_id) is int:
            member_id = str(member_id)
        # 这里必须用utcnow否则会引发jwt.InvalidTokenError
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'sub': member_id
        }
        return jwt.encode(payload, cls.secret, algorithm='HS256')
    
    @classmethod
    def decode_token(cls, token) -> int:
        try:
            payload = jwt.decode(token, cls.secret, algorithms=['HS256'])
            return int(payload['sub'])
        except jwt.ExpiredSignatureError:
            raise AuthError(detail='Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthError(detail='Invalid token')
    
    @classmethod
    def auth_wrapper(cls, auth: HTTPAuthorizationCredentials = Security(security)) -> int:
        return cls.decode_token(auth.credentials)  # user_id


auth = APIRouter()


# @auth.post("/register")
# async def register(auth_user: AuthUser):
#     if any(user['username'] == auth_user.username for user in users):
#         return normal_resp.fail(status=400, message='Username already exists')
#     hashed_password = AuthHandler.get_password_hash(auth_user.password)
#     users.append({'username': auth_user.username, 'password': hashed_password})
#     return normal_resp.success({})


@auth.post("/password/update", description="更新密码")
async def change_password(password: Password, member_id: int = Depends(AuthHandler.auth_wrapper)):
    password = password.password
    member_id = await MemberValidator(member_id)
    try:
        await Member.filter(id=member_id).update(password=AuthHandler.get_password_hash(password))
        return normal_resp.success({})
    except:
        raise AuthError(detail='更新密码失败')


# 权限校验, 只能高级成员重置低级成员
# @auth.post("/password/reset", description="重置密码")
# async def reset_password(member_id: int = Depends(AuthHandler.auth_wrapper)):
#     pass


@auth.post("/login", description="登录接口, 请求有身份校验的接口时须有 {'authorization': token} 字段")
async def login(input_user: AuthUser):
    # 通过id登录或者通过姓名登录
    if type(input_user.username) is int:
        try:
            user: dict = await Member.get(id=input_user.username).values('id', 'password')
        except:
            return normal_resp.fail(status=400, message='Invalid username or password')
    else:
        try:
            user: dict = await Member.get(name=input_user.username).values('id', 'password')
        except MultipleObjectsReturned:
            return normal_resp.fail(status=400, message='有重名, 请用id登录')
        except:
            return normal_resp.fail(status=400, message='Invalid username or password')
    
    if not AuthHandler.verify_password(input_user.password, user['password']):
        return normal_resp.fail(status=400, message='Invalid username or password')
    token = AuthHandler.encode_token(user['id'])
    return normal_resp.success({'token': 'Bearer ' + token})
