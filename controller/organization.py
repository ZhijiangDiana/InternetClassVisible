import json

from fastapi import APIRouter
from pydantic import BaseModel, validator

from entity.db_entity import *

organization = APIRouter()


@organization.post("/add_all")
async def add_all():
    with open(f"all_organization.json", "r", encoding="utf-8") as all_organization:
        all_organization = json.load(all_organization)
        for one_org in all_organization["result"]:
            added_org = await Organization.create(id=one_org["id"], pid=one_org["pid"], title=one_org["title"],
                                                  qr_code=one_org["qrCode"])
            print(added_org)

    return True
