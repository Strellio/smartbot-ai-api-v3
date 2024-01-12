from datetime import datetime
from bson.objectid import ObjectId
from app.lib.db import ticketModel
from enum import Enum
from nanoid import generate


class TICKET_PRIORITY_ENUM(Enum):
    HIGH = 'high'
    LOW = 'low'
    MEDIUM = 'medium'


def createTicket(business_id, customer_id, chat_platform_id, email, order_number, order_id, priority: TICKET_PRIORITY_ENUM, description, title):
    input = {
        "business": ObjectId(business_id),
        "order_number": order_number,
        "title": title,
        "customer": ObjectId(customer_id),
        "order_id": order_id,
        "source": ObjectId(chat_platform_id),
        "description": description,
        "priority": priority.value,
        "order_email": email,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "ticket_number": generate('1234567890', 8),
        "column_id": 1

    }
    result = ticketModel.insert_one(input)
    return {
        "_id": result.inserted_id,
        **input
    }
