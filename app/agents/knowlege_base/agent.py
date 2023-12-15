
from typing import Any
from langchain.chat_models import ChatOpenAI
from pydantic import Field, BaseModel
from langchain.agents import AgentExecutor
from app.agents.knowlege_base.tools import getTools
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from app.utils.llm import getLLM

from app.utils.memory import getMemory


class KnowledgeBaseAgent(BaseModel):
    knowledge_base_agent: Any = Field(...)
    user_input: str

    @classmethod
    def init(self, llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=10, user_input='') -> "KnowledgeBaseAgent":

        tools = getTools(llm=getLLM(model_name="gpt-4"), memory=memory, verbose=verbose, business=business, customer=customer, chat_platform=chat_platform,
                         max_iterations=max_iterations, user_input=user_input)

        system_message = SystemMessage(
            content=(
                """
    Never forget you work as a shopping assistant for an online store. You are part of the Knowlegdge base team. You are responsible for providing answers to some 

    1. frequently ask questions, 
    2.information about our return and refund policy, 
    3. terms of service,
    4 shipping policy, 
    5. order cancellation policy, 
    6. promotions and discounts
    7. and contact information.



    You don't have any knowledge about the above listed information so you must always use a tool for it

    You must respond according to the tool response.

    Your response must be concise, clear and straight to the point. Don't apologize to the customer.

    """
            )
        )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")])

        agent = OpenAIFunctionsAgent(
            llm=getLLM(model_name="gpt-4"), tools=tools, prompt=prompt)

        knowledge_base_agent = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=verbose, max_iterations=max_iterations, memory=getMemory(session_id=customer.get("_id"), db_name=business.get("account_name"),
                                                                                                       memory_key="chat_history", return_messages=True)

        )

        return self(knowledge_base_agent=knowledge_base_agent,  user_input=user_input)

    def run(self, input: str):
        return self.knowledge_base_agent.run(input=input)
