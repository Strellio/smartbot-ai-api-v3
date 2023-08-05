from bson.objectid import ObjectId
from app.models import InputMetadata
from app.lib.db import (businessModel, chatPlatformModel)


def getBusinessBy(id):
    business = businessModel.find_one({"_id": ObjectId(id)})
    return business


def getChatPlatformByIdAndBusinessId(id, businessId):
    business = chatPlatformModel.find_one(
        {"_id": ObjectId(id), "business": ObjectId(businessId)})
    return business


# GetBusiness and chat platform
def getBusinessAndChatPlatform(metadata: InputMetadata) -> tuple:
    businessId = metadata.business_id
    chatPlatformId = metadata.chat_platform_id
    business = getBusinessBy(businessId)
    chatPlatform = getChatPlatformByIdAndBusinessId(
        chatPlatformId, business.get("_id"))
    return business, chatPlatform
