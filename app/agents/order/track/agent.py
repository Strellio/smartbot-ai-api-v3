
from typing import Union
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from pydantic import Field, BaseModel
from app.agents.order.track.parser import OrderTrackOutputParser
from langchain.agents import LLMSingleActionAgent, AgentExecutor
from app.agents.order.track.prompt import getOrderTrackingPrompt
from app.agents.order.track.tools import getTools
from langchain.memory import ReadOnlySharedMemory, ConversationBufferMemory


class OrderTrackAgent(BaseModel):
    order_track_agent: Union[AgentExecutor, None] = Field(...)
    llm_chain: Union[LLMChain, None] = Field(...)
    user_input: str
    memory: ConversationBufferMemory = Field(...)

    @classmethod
    def init(self, llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=10, user_input='') -> "OrderTrackAgent":

        tools = getTools(llm=llm, memory=ReadOnlySharedMemory(memory=memory), verbose=verbose, business=business, customer=customer, chat_platform=chat_platform,
                         max_iterations=max_iterations, user_input=user_input)

        tool_names = [tool.name for tool in tools]

        llm_chain = LLMChain(
            llm=llm, prompt=getOrderTrackingPrompt(tools=tools))

        order_track_agent_with_tools = LLMSingleActionAgent(
            output_parser=OrderTrackOutputParser(
                business=business, customer=customer, chat_platform=chat_platform),
            llm_chain=llm_chain,
            stop=["\Observation:"],
            allowed_tools=tool_names,
            verbose=verbose,
            max_iterations=max_iterations,
        )

        order_track_agent = AgentExecutor.from_agent_and_tools(
            agent=order_track_agent_with_tools, tools=tools, verbose=verbose, max_iterations=max_iterations, memory=memory

        )

        return self(order_track_agent=order_track_agent, llm_chain=llm_chain, user_input=user_input, memory=memory)

    def run(self, input: str):
        print("user input", self.user_input)
        return self.order_track_agent.run(input=input)
