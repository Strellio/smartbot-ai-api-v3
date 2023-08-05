from lib.db import db
from bson.objectid import ObjectId
from app.lib.db import customerModel


def talkToAgent(customerId: str):
    result = customerModel.update_one({"_id": ObjectId(customerId)}, {
                                      "$set": {"is_chat_with_live_agent": True}})
    return result
