
from enum import Enum

from app.services.tickets.create_ticket import TICKET_PRIORITY_ENUM


class TicketType(Enum):
    ORDER_CANCELLATION = "order-cancel"
    ORDER_RETURN = "order-return"
    ORDER_REFUND = "order-refund"
    ORDER_DELAY = "order-delay"
    ORDER_RESCHEDULE = "order-reschedule"
    ORDER_ADDRESS_CHANGE = "order-address-change"
    ORDER_INCOMPLETE = "order-incomplete"
    ORDER_PAYMENT_ISSUE = "order-payment-issue"
    ORDER_PAYMENT_CHANGE = "order-payment-change"
    ORDER_INCORRECT = "order-incorrect"
    ORDER_DELIVERY_ISSUE = "order-delivery-issue"


def generateTicketPayload(order_id: str, ticket_type: TicketType, **kwargs):
    ticket_descriptions = {
        TicketType.ORDER_CANCELLATION.value: lambda kwargs:  ("Order Cancellation", f"Order {order_id} cancellation due to {kwargs.get('cancellationReason')}.", TICKET_PRIORITY_ENUM.MEDIUM),
        TicketType.ORDER_RETURN.value: lambda kwargs:  ("Order Return", f"Order {order_id} return due to {kwargs.get('returnReason')}.", TICKET_PRIORITY_ENUM.MEDIUM),
        TicketType.ORDER_REFUND.value: lambda kwargs:  ("Order Refund", f"Order {order_id} refund due to {kwargs.get('refundReason')}.", TICKET_PRIORITY_ENUM.MEDIUM),
        TicketType.ORDER_DELAY.value: lambda kwargs:  ("Order Delivery Delay", f"Order {order_id} delivery delay. Expected delivery date: {kwargs.get('pastDeliveryDate')}.", TICKET_PRIORITY_ENUM.MEDIUM),
        TicketType.ORDER_RESCHEDULE.value: lambda kwargs:  ("Order Delivery Reschedule", f"Order {order_id} delivery rescheduled to {kwargs.get('newDeliveryDate')} due to {kwargs.get('rescheduleReason')}.", TICKET_PRIORITY_ENUM.HIGH),
        TicketType.ORDER_ADDRESS_CHANGE.value: lambda kwargs:  ("Order Delivery Address Change", f"Order {order_id} delivery address changed to {kwargs.get('newDeliveryAddress')}.", TICKET_PRIORITY_ENUM.HIGH),
        TicketType.ORDER_INCOMPLETE.value: lambda kwargs:  ("Incomplete Order", f"Order {order_id} is incomplete due to missing items: {kwargs.get('missingItems')}.", TICKET_PRIORITY_ENUM.HIGH),
        TicketType.ORDER_PAYMENT_ISSUE.value: lambda kwargs:  ("Order Payment Issue", f"Order {order_id} payment issue with {kwargs.get('paymentMethod')}.", TICKET_PRIORITY_ENUM.HIGH),
        TicketType.ORDER_PAYMENT_CHANGE.value: lambda kwargs:  ("Order Payment Method Change", f"Order {order_id} payment method changed to {kwargs.get('newPaymentMethod')} due to {kwargs.get('paymentMethodChangeReason')}.", TICKET_PRIORITY_ENUM.MEDIUM),
        TicketType.ORDER_INCORRECT.value: lambda kwargs:  ("Incorrect Order", f"Order {order_id} is incorrect. Incorrect items: {kwargs.get('incorrectItems')}."),
        TicketType.ORDER_DELIVERY_ISSUE.value: lambda kwargs:  (
            "Order Delivery Issue", f"Order {order_id} has a delivery issue: {kwargs.get('deliveryIssue')}.", TICKET_PRIORITY_ENUM.MEDIUM),
    }

    print(ticket_type in ticket_descriptions, "ticket_type")

    if ticket_type in ticket_descriptions:
        description_function = ticket_descriptions[ticket_type]
        title, description, priority = description_function(kwargs)
        return {
            "order_id": order_id,
            # "type": ticket_type,
            "order_number": order_id,
            "title": title,
            "description": description,
            "priority": priority
        }
    else:
        return {}
