
from typing import Union
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from pydantic import Field, BaseModel
from app.agents.product.search.parser import ProductKnowledgeBaseOutputParser
from langchain.agents import LLMSingleActionAgent, AgentExecutor
from app.agents.product.search.prompt import getProductKnowlegeBasePrompt
from app.agents.product.search.tools import getTools
from langchain.memory import ConversationBufferMemory

from langchain.agents.agent_toolkits import create_conversational_retrieval_agent

from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder

from app.utils.memory import getMemory


class ProductKnowledgeBaseAgent(BaseModel):
    product_knowledge_base_agent: Union[AgentExecutor, None] = Field(...)
    llm_chain: Union[LLMChain, None] = Field(...)
    user_input: str
    memory: ConversationBufferMemory = Field(...)

    @classmethod
    def init(self, llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=10, user_input='') -> "ProductKnowledgeBaseAgent":

        tools = getTools(llm=llm, memory=memory, verbose=verbose, business=business, customer=customer, chat_platform=chat_platform,
                         max_iterations=max_iterations, user_input=user_input)

        tool_names = [tool.name for tool in tools]

        llm_chain = LLMChain(
            llm=llm, prompt=getProductKnowlegeBasePrompt(tools=tools))

        # product_knowledge_base_agent = create_conversational_retrieval_agent(
        #     llm, tools, verbose=True, remember_intermediate_steps=False)
        system_message = SystemMessage(
            content=(
                "Do your best to answer the questions. "
                "Feel free to use any tools available to look up "
                "You are not good at searching for products or have any knowlege about the product that we sell  so you must always use a tool for it"
                "relevant information, only if neccessary"
                "return the tool respponse to the customer as your response"

            )
        )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")])

        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

        product_knowledge_base_agent_with_tools = LLMSingleActionAgent(
            output_parser=ProductKnowledgeBaseOutputParser(
                business=business, customer=customer, chat_platform=chat_platform),
            llm_chain=llm_chain,
            stop=["\Observation:"],
            allowed_tools=tool_names,
            verbose=verbose,
            max_iterations=max_iterations,
        )

        product_knowledge_base_agent = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=verbose, max_iterations=max_iterations, memory=getMemory(session_id=customer.get("_id"), db_name=business.get("account_name"),
                                                                                                       memory_key="chat_history", return_messages=True)

        )

        return self(product_knowledge_base_agent=product_knowledge_base_agent, llm_chain=llm_chain, user_input=user_input, memory=memory)

    def run(self, input: str):
        print("user input", self.user_input)
        return self.product_knowledge_base_agent.run(input=input)
