
from typing import Union
from langchain import LLMChain, ConversationChain
from pydantic import Field, BaseModel
from app.agents.order.tickets.parser import SupportTicketOutputParser
from langchain.agents import LLMSingleActionAgent, AgentExecutor
from app.utils.llm import getLLM
from app.agents.order.tickets.prompt import order_ticket_prompt
from app.agents.order.tickets.tools import support_ticket_tools, support_ticket_tools_names


class OrderTicketAgent(BaseModel):
    order_ticket_agent: Union[AgentExecutor, None] = Field(...)
    llm_chain: Union[LLMChain, None] = Field(...)

    @classmethod
    def init(self, memory, verbose=False, max_iterations=3) -> "OrderTicketAgent":
        llm_chain = LLMChain(
            llm=getLLM(), prompt=order_ticket_prompt)

        order_action_with_tools = LLMSingleActionAgent(
            output_parser=SupportTicketOutputParser(),
            llm_chain=llm_chain,
            stop=["\nObservation:"],
            allowed_tools=support_ticket_tools_names,
            verbose=verbose,
        )

        order_ticket_agent = AgentExecutor.from_agent_and_tools(
            agent=order_action_with_tools, tools=support_ticket_tools, verbose=verbose, max_iterations=max_iterations, memory=memory

        )

        return self(order_ticket_agent=order_ticket_agent, llm_chain=llm_chain)

    def run(self, input: str):
        return self.order_ticket_agent.run(input)
