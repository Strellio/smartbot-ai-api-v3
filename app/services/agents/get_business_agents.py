from lib.db import db
from bson.objectid import ObjectId
from models import agentsModel


def getBusinessOnlineAgents(businessId: str):
    onlineAgents = agentsModel.find_one(
        {"business": ObjectId(businessId), "is_online": True})
    return onlineAgents
