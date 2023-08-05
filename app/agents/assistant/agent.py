

from langchain import LLMChain
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.chains.base import Chain
from pydantic import BaseModel, Field
from typing import Union, Any
from app.agents.assistant.parser import ShopAssistantOutputParser
from app.agents.assistant.prompt import getShopAssistantPrompt
from langchain.agents import LLMSingleActionAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from app.agents.assistant.tools import getTools


class ShopAssistant(BaseModel):
    business: Any = Field(...)
    memory: ConversationBufferMemory = Field(...)
    shop_assistant_executor: Union[AgentExecutor, None] = Field(...)

    @classmethod
    def init(self, llm: ChatOpenAI, memory: ConversationBufferMemory, business, chatPlatform, verbose=False, max_iterations=3):

        tools = getTools(llm=llm, memory=memory, verbose=verbose, business=business,
                         max_iterations=max_iterations)

        tool_names = [tool.name for tool in tools]

        prompt = getShopAssistantPrompt(tools)

        llm_chain = LLMChain(llm=llm, prompt=prompt)

        output_parser = ShopAssistantOutputParser(verbose=verbose)

        shop_assistant_with_tools = LLMSingleActionAgent(
            llm_chain=llm_chain,
            output_parser=output_parser,
            stop=["\nObservation:"],
            allowed_tools=tool_names,
            verbose=verbose,
            max_iterations=max_iterations,

        )

        shop_assistant_executor = initialize_agent(
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            tools=tools,
            llm=llm,
            verbose=verbose,
            max_iterations=max_iterations,
            memory=memory,
            # agent_kwargs={"output_parser": output_parser}
        )

        # shop_assistant_executor = AgentExecutor.from_agent_and_tools(
        #     agent=shop_assistant_with_tools, tools=tools, verbose=verbose, max_iterations=max_iterations, memory=memory
        # )

        return self(shop_assistant_executor=shop_assistant_executor, memory=memory, business=business, max_iterations=max_iterations)

    def run(self, input):
        ouput = self.shop_assistant_executor.run(
            input=input,
            chat_history=self.memory.load_memory_variables({})[
                "chat_history"],
            # shop_name=self.shop.get("name"),
        )
        return ouput
