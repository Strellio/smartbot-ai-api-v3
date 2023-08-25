from bson import ObjectId
from app.lib.db import customerModel


def getCustomer(query):
    return customerModel.find_one(query)


def getCustomerId(customer_id):
    return customerModel.find_one({"_id": ObjectId(customer_id)})


def getCustomerByPlatform(customer_id, platform):
    if platform != "custom":
        print("is not custom")
        return getCustomer({"external_id": customer_id})
    else:
        print("is custom")
        return getCustomer({"_id": ObjectId(customer_id)})
