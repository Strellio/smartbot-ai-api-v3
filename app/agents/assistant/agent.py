

from langchain import LLMChain
from langchain.chains.base import Chain
from pydantic import BaseModel, Field
from typing import Union, Any
from app.agents.assistant.parser import ShopAssistantOutputParser
from app.agents.assistant.prompt import getShopAssistantPrompt
from langchain.agents import LLMSingleActionAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from app.agents.assistant.tools import getTools
from app.utils.llm import getLLM


class ShopAssistant(BaseModel):
    shop: Any = Field(...)
    memory: ConversationBufferMemory = Field(...)
    shop_assistant_executor: Union[AgentExecutor, None] = Field(...)

    @classmethod
    def init(self, memory: ConversationBufferMemory, shop, verbose=False, max_iterations=3):

        tools = getTools(memory=ReadOnlySharedMemory(memory=memory), verbose=verbose,
                         max_iterations=max_iterations)

        tool_names = [tool.name for tool in tools]

        prompt = getShopAssistantPrompt(tools)

        llm_chain = LLMChain(llm=getLLM(), prompt=prompt)

        output_parser = ShopAssistantOutputParser(verbose=verbose)

        shop_assistant_with_tools = LLMSingleActionAgent(
            llm_chain=llm_chain,
            output_parser=output_parser,
            stop=["\nObservation:"],
            allowed_tools=tool_names,
            verbose=verbose,
            max_iterations=max_iterations,
        )

        shop_assistant_executor = AgentExecutor.from_agent_and_tools(
            agent=shop_assistant_with_tools, tools=tools, verbose=verbose
        )

        return self(shop_assistant_executor=shop_assistant_executor, memory=memory, shop=shop, max_iterations=max_iterations)

    def run(self, input):
        self.memory.chat_memory.add_user_message(input)
        ouput = self.shop_assistant_executor.run(
            input=input,
            conversation_history=self.memory.load_memory_variables({})[
                "conversation_history"],
            shop_name=self.shop.get("name"),
        )
        self.memory.chat_memory.add_ai_message(ouput)
        return ouput
