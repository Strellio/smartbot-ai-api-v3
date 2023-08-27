
from typing import Union
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from pydantic import Field, BaseModel
from app.agents.tickets.status.parser import SupportTicketStatusOutputParser
from langchain.agents import LLMSingleActionAgent, AgentExecutor
from app.agents.tickets.status.prompt import ticket_status_prompt


class TicketStatusAgent(BaseModel):
    ticket_status_agent: Union[AgentExecutor, None] = Field(...)
    llm_chain: Union[LLMChain, None] = Field(...)

    @classmethod
    def init(self, llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=10) -> "TicketStatusAgent":
        llm_chain = LLMChain(
            llm=llm, prompt=ticket_status_prompt)

        ticket_status_with_tools = LLMSingleActionAgent(
            output_parser=SupportTicketStatusOutputParser(
                business=business, customer=customer, chat_platform=chat_platform),
            llm_chain=llm_chain,
            stop=["\nObservation:"],
            allowed_tools=[],
            verbose=verbose,

            max_iterations=max_iterations,
        )

        ticket_status_agent = AgentExecutor.from_agent_and_tools(
            agent=ticket_status_with_tools, tools=[
            ], verbose=verbose, max_iterations=max_iterations, memory=memory

        )

        return self(ticket_status_agent=ticket_status_agent, llm_chain=llm_chain)

    def run(self, input: str):
        return self.ticket_status_agent.run(input)
