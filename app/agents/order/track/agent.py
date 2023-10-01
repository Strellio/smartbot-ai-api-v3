
from typing import Any
from langchain.chat_models import ChatOpenAI
from pydantic import Field, BaseModel
from langchain.agents import AgentExecutor
from app.agents.order.track.tools import getTools
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder

from app.utils.memory import getMemory


class OrderTrackAgent(BaseModel):
    order_track_agent: Any = Field(...)
    user_input: str

    @classmethod
    def init(self, llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=10, user_input='') -> "OrderTrackAgent":

        tools = getTools(llm=llm, memory=memory, verbose=verbose, business=business, customer=customer, chat_platform=chat_platform,
                         max_iterations=max_iterations, user_input=user_input)

        system_message = SystemMessage(
            content=(
                """
Never forget you work as a shopping assistant that helps customers to get update on their orders and also track them. You are friendly and supportive as well.



The customer must provide the following required details:
1. the order email (required)
2. the order number (required)

PLEASE don't use your own placeholders like  [customer's email], and [order number] as the values to the input.

Let the customers be the one to provide them


if you don't have any of the information listted above from the customer you must  ask for it from the customer. If you have only the email from the customer you must request the order number and vice versa.

After taking the order number and email from the customer you need to use a tool to search for the order with the email and the orderNumber as the input

You are not good at giving order updates and tracking order so you must always use a tool for it

Do not generate any hypothetical conversations. You must have a real conversation with the customer.

You must respond according to the tool response.

Don't send  links or urls like this [link] or [tracking URL] to the customer. Just always return the full and correct url you got from the tool response to the customer.

 """
            )
        )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")])

        agent = OpenAIFunctionsAgent(
            llm=llm, tools=tools, prompt=prompt)

        order_track_agent = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=verbose, max_iterations=max_iterations, memory=getMemory(session_id=customer.get("_id"), db_name=business.get("account_name"),
                                                                                                       memory_key="chat_history", return_messages=True)

        )

        return self(order_track_agent=order_track_agent,  user_input=user_input)

    def run(self, input: str):
        return self.order_track_agent.run(input=input)
