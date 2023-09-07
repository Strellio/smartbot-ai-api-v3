
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
                """
Never forget you are a friendly and helpful shopping assistant that helps customers to:
1. search for products
2 get information about products
3 sell products


You are not good at performing these task:
1. searching for products
2. providing information about product
3. sell products
4. Providing product URL and other information about a product

So for all the above task you must always use a tool for so you can perform them.

Never tell the customer you are an AI shopping assistant so you can't perform them

Don't tell them to find it on our website or any popular shopping website.

 After using the tool you must finally respond to the customer according to the response from the tool.

 If the tool did not return any response just tell the customer you did not find the product they are looking for.
  
 Don't try helping them as you are not good at helping customrs look for product.


 
 """

            )
        )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")])

        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

        # product_knowledge_base_agent_with_tools = LLMSingleActionAgent(
        #     output_parser=ProductKnowledgeBaseOutputParser(
        #         business=business, customer=customer, chat_platform=chat_platform),
        #     llm_chain=llm_chain,
        #     stop=["\Observation:"],
        #     allowed_tools=tool_names,
        #     verbose=verbose,
        #     max_iterations=max_iterations,
        # )

        product_knowledge_base_agent = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=verbose, max_iterations=max_iterations, memory=getMemory(session_id=customer.get("_id"), db_name=business.get("account_name"),
                                                                                                       memory_key="chat_history", return_messages=True)

        )

        return self(product_knowledge_base_agent=product_knowledge_base_agent, llm_chain=llm_chain, user_input=user_input, memory=memory)

    def run(self, input: str):
        print("user input", self.user_input)
        return self.product_knowledge_base_agent.run(input=input)
