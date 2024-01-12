
from typing import Any
from langchain.chat_models import ChatOpenAI
from pydantic import Field, BaseModel
from langchain.agents import AgentExecutor

from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder

from langchain.tools import StructuredTool
from app.agents.tickets.status.utils import generateTicketResponseBaseOnColumnID

from app.services.tickets.get_ticket import getTicket
from app.utils.memory import getMemory


def ticketStatus(customerId):
    def getTicketByTicketNumber(ticketNumber):
        print(ticketNumber)
        ticket = getTicket(customerId, f"{ticketNumber}")
        if not ticket:
            return f"I could not find any support ticket of yours with number {ticketNumber}. Kindly recheck and try again"
        else:
            return generateTicketResponseBaseOnColumnID(ticket)
    return getTicketByTicketNumber


class TicketStatusAgent(BaseModel):
    ticket_status_agent: Any = Field(...)
    user_input: str

    @classmethod
    def init(self, llm: ChatOpenAI, memory, business, customer, chat_platform, user_input, verbose=False, max_iterations=10) -> "TicketStatusAgent":

        system_message = SystemMessage(
            content=(
                """
                You are a assistant that assists customers to follow up on their support ticket to get update on it. 

                The customer has to provide the ticketNumber in order for you to help identify the exact support ticket.

                Always request for a new ticketNumber from the customer for every follow up.

                Remember, do not generate any hypothetical conversations. You must have a real conversation with the customer.

                Never tell the customer to contact the support team directly. 

                Your response must be concise, clear and straight to the point. Don't apologize to the customer.

                After taking the ticket number use a tool to get the ticket details 

                """

            )
        )

        tools = [
            StructuredTool.from_function(
                name="CheckStatusOfCreatedSupportTicket",
                func=ticketStatus(customer.get("_id")),
                return_direct=False,
                description="useful for when you need to check the status or follow up on a support ticket",
                # description="useful for when you need to answer questions about order information, getting status and update for orders",
            )
        ]

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")])

        agent = OpenAIFunctionsAgent(
            llm=llm, tools=tools, prompt=prompt)

        ticket_status_agent = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=verbose, max_iterations=max_iterations, memory=getMemory(session_id=customer.get("_id"), db_name=business.get("account_name"),
                                                                                                       memory_key="chat_history", return_messages=True)
        )

        return self(ticket_status_agent=ticket_status_agent, user_input=user_input)

    def run(self, input: str):
        return self.ticket_status_agent.run(input)
