# pip install pyjwt
# pip install passlib[bcrypt]
# pip install bcrypt==4.0.1

import jwt
from fastapi import Depends, Security, APIRouter
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from entity.input_model import AuthUser
from entity.response import normal_resp
from middleware.ExceptionHandler import AuthError


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = 'SECRET'

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def encode_token(self, user_id):
        # 这里必须用utcnow否则会引发jwt.InvalidTokenError
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')
    
    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise AuthError(detail='Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthError(detail='Invalid token')
    
    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)  # user_id


auth = APIRouter()
auth_handler = AuthHandler()

# TODO Tortoise orm
users = []


@auth.post("/register")
def register(auth_user: AuthUser):
    if any(user['username'] == auth_user.username for user in users):
        return normal_resp.fail(status=400, message='Username already exists')
    hashed_password = auth_handler.get_password_hash(auth_user.password)
    users.append({'username': auth_user.username, 'password': hashed_password})
    return normal_resp.success({})


@auth.post("/login")
def login(auth_user: AuthUser):
    user = None
    for u in users:
        if u['username'] == auth_user.username:
            user = u
            break
    if (user is None) or (not auth_handler.verify_password(auth_user.password, user['password'])):
        return normal_resp.fail(status=400, message='Invalid username or password')
    token = auth_handler.encode_token(user['username'])
    return normal_resp.success({'token': token})


# usage

# @auth.get("/unprotected")
# def unprotected():
#     return {"hello": "world"}


@auth.get("/protected")
def protected(user_id=Depends(auth_handler.auth_wrapper)):
    return {'user_id': user_id}