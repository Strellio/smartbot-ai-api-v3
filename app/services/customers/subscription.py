from datetime import datetime
from lib.db import db
from bson.objectid import ObjectId
from models import customerModel
from services.customers import updateCustomer


def getSubcription(query):
    document = customerModel.find_one(query)
    return document


def checkIfUserIsSubscribed(business_id, customer_id):
    result = getSubcription(
        {"business": ObjectId(business_id), "_id": ObjectId(customer_id)})
    if not result:
        return False
    else:
        return result["subscribed"]


def handleUpsertSubscription(business_id, customer_id,  subscribed, email):
    result = updateCustomer(query={
        "business": ObjectId(business_id),
        "_id": ObjectId(customer_id),
    }, update={
        "subscribed": subscribed,
        "last_subscribe_asked": datetime.now(),
        "email": email,

    })
    return result
