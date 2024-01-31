import json

from fastapi import APIRouter
from pydantic import BaseModel, validator

from entity.db_entity import *

test = APIRouter()

