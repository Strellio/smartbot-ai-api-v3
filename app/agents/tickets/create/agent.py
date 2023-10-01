
from typing import Any
from langchain.chat_models import ChatOpenAI
from pydantic import Field, BaseModel
from langchain.agents import AgentExecutor

from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.tools import StructuredTool

from app.agents.tickets.create.utils import generateTicketPayload
from app.services.tickets.create_ticket import createTicket
from app.utils.memory import getMemory


def createSupportTicketTool(customer, business, chat_platform):
    def createSupportTicket(payload):
        ticketInfo = generateTicketPayload(order_id=payload.get(
            "orderID"), ticket_type=payload.get("type"), **payload)

        result = createTicket(customer_id=customer.get("_id"), business_id=business.get(
            "_id"), chat_platform_id=chat_platform.get("_id"), email=customer.get("email"), **ticketInfo)
        return f"I have created a support ticket for you. Your support ticket number is {result.get('ticket_number')}. Our team will get in touch with you to resolve your {ticketInfo.get('title')} request"

    return createSupportTicket


class OrderTicketAgent(BaseModel):
    order_ticket_agent: Any = Field(...)
    user_input: str

    @classmethod
    def init(self, llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=10, user_input='') -> "OrderTicketAgent":

        system_message = SystemMessage(
            content=(
                """
You are an assistant that assists customers to create order support tickets. 

The customer has to provide some required fields depending on the type of support ticket they want to create.

Below are the types of support tickets you can create and the required fields:
1. Order cancellation: orderID and cancellationReason are the required fields, and the type is "order-cancel."
2. Order return: orderID and returnReason are the required fields, and the type is "order-return."
3. Order refund: orderID and refundReason are the required fields, and the type is "order-refund."
4. Order delivery delay: orderID and pastDeliveryDate are the required fields, and the type is "order-delay."
5. Order delivery reschedule: orderID, rescheduleReason, newDeliveryDate are the required fields, and the type is "order-reschedule."
6. Order delivery address change: orderID and newDeliveryAddress are the required fields, and the type is "order-address-change."
7. Incomplete order: orderID and missingItems are the required fields, and the type is "order-incomplete."
8. Order payment issue: orderID and paymentMethod are the required fields, and the type is "order-payment-issue."
9. Order payment method change: orderID, newPaymentMethod, and paymentMethodChangeReason are the required fields, and the type is "order-payment-change."
10. Incorrect order: orderID and incorrectItems are the required fields, and the type is "order-incorrect."
11. Order delivery issue: orderID and deliveryIssue are the required fields, and the type is "order-delivery-issue."


Before doing so, review the conversation history only after the customer's latest support request to identify the fields. If not, you should request them from the customer.

Never tell the customer to contact the support team directly. 

You must respond according to the previous chat history.

After taking the required fields from the customer, use a tool to create the support ticket

                """

            )
        )

        tools = [
            StructuredTool.from_function(
                name="CreateNewSupportTicket",
                func=createSupportTicketTool(
                    customer=customer, business=business, chat_platform=chat_platform),
                return_direct=False,
                description="useful for when you need to create a support ticket for an issue a customer is reporting about their order. This is when a customer report an issue to you.",
            )
        ]

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")])

        agent = OpenAIFunctionsAgent(
            llm=llm, tools=tools, prompt=prompt)

        order_ticket_agent = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=verbose, max_iterations=max_iterations,  memory=getMemory(session_id=customer.get("_id"), db_name=business.get("account_name"),
                                                                                                        memory_key="chat_history", return_messages=True)

        )

        return self(order_ticket_agent=order_ticket_agent, user_input=user_input)

    def run(self, input: str):
        return self.order_ticket_agent.run(input)
