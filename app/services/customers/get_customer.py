from bson import ObjectId
from app.lib.db import customerModel


def getCustomer(query):
    return customerModel.find_one(query)


def getCustomerId(customer_id):
    return customerModel.find_one({"_id": ObjectId(customer_id)})
