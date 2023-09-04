def generateTicketResponseBaseOnColumnID(ticket):
    map_column_id_status = {
        1: f"Your {ticket.get('title')}  support ticket is yet to be resolved. Kindly exercise some patience for us to resolve this as soon as possible",
        2: f"Our support team needs some help from you in order to resolve your {ticket.get('title')} request for you. Kindly reach out to our support team to help them resolve your request",
        3: f"Our support team is currently working on your {ticket.get('title')} request. You will be notified when it is finally resolved",
        4: f"Your {ticket.get('title')} support request has been successfully resolved. Thanks for your patience."
    }
    column_id = ticket.get("column_id")

    return map_column_id_status.get(column_id, f"Your {ticket.get('title')}  support ticket is yet to be resolved. Kindly exercise some patience for us to resolve this as soon as possible")
