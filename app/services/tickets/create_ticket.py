from datetime import datetime
from lib.db import db
from bson.objectid import ObjectId
from models import ticketModel
from enum import Enum


class TICKET_PRIORITY_ENUM(Enum):
    HIGH = 'high',
    LOW = 'low',
    MEDIUM = 'medium'


def createTicket(business_id, customer_id, chat_platform_id, email, order_number, order_id, priority: TICKET_PRIORITY_ENUM, description, title):
    result = ticketModel.insert_one({
        "business": ObjectId(business_id),
        "order_number": order_number,
        "title": title,
        "customer": ObjectId(customer_id),
        "order_id": order_id,
        "source": ObjectId(chat_platform_id),
        "description": description,
        "priority": str(priority),
        "order_email": email,
        "created_at": datetime.now(),
        "updated_at": datetime.now()

    })
    return result
