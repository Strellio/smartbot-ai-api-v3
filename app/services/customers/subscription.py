from datetime import datetime
from app.lib.db import db
from bson.objectid import ObjectId
from app.lib.db import customerModel
from app.services.customers import updateCustomer
from app.services.customers.get_customer import getCustomer


def checkIfUserIsSubscribed(business_id, customer_id):
    result = getCustomer(
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
