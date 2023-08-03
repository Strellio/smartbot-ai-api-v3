

from langchain import LLMChain
from app.agents.order.tickets.parser import SupportTicketOutputParser
from langchain.agents import LLMSingleActionAgent, AgentExecutor
from app.utils.llm import getLLM
from tools import support_ticket_tools, support_ticket_tools_names
from prompt import order_ticket_prompt


class OrderTicketAgent():
    def executor(self, memory, verbose=False, max_iterations=3):
        llm_chain = LLMChain(llm=getLLM(), prompt=order_ticket_prompt)

        order_action_with_tools = LLMSingleActionAgent(
            output_parser=SupportTicketOutputParser(),
            llm_chain=llm_chain,
            stop=["\nObservation:"],
            allowed_tools=support_ticket_tools_names,
            verbose=verbose,
        )

        return AgentExecutor.from_agent_and_tools(
            agent=order_action_with_tools, tools=support_ticket_tools, verbose=verbose, max_iterations=max_iterations, memory=memory

        )
