import requests
from lib.db import db
from bson.objectid import ObjectId
from os import getenv
from models import (businessModel, chatPlatformModel)


def getBusinessBy(id):
    business = businessModel.find_one({"_id": ObjectId(id)})
    return business


def getChatPlatformByIdAndBusinessId(id, businessId):
    business = chatPlatformModel.find_one(
        {"_id": ObjectId(id), "business": ObjectId(businessId)})
    return business


# GetBusiness and chat platform
def getBusinessAndChatPlatform(metadata) -> tuple:
    businessId = metadata.get("business_id", getenv("TEST_BUSINESS_ID"))
    chatPlatformId = metadata.get(
        "chat_paltform_id", getenv("TEST_CHAT_PLATFORM_ID"))
    business = getBusinessBy(businessId)
    chatPlatform = getChatPlatformByIdAndBusinessId(
        chatPlatformId, business.get("_id"))
    return business, chatPlatform
