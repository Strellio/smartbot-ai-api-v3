from app.lib.db import db
from bson.objectid import ObjectId
from app.lib.db import agentsModel


def getBusinessOnlineAgent(businessId: str):
    onlineAgents = agentsModel.find_one(
        {"business": ObjectId(businessId), "availability_status": "available", "status": "A"})
    return onlineAgents
