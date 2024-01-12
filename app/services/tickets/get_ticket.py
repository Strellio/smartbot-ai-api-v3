from app.lib.db import ticketModel
from bson.objectid import ObjectId


def getTicket(customer_id: str, ticket_number: str):
    return ticketModel.find_one({"customer": ObjectId(customer_id), "ticket_number": ticket_number})
