from datetime import datetime
from app.lib.db import customerModel


def updateCustomer(query, update):
    updated_at = {"updated_at": datetime.now()}
    update_data = {key: val for key,
                   val in update.items() if key is not None}
    result = customerModel.update_one(
        query, {"$set": {**update_data, **updated_at}})
    return result
