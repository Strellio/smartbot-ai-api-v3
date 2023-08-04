from langchain.agents import load_tools, Tool
from langchain.chat_models import ChatOpenAI

from app.agents.order.tickets.agent import OrderTicketAgent


def getTools(llm: ChatOpenAI, memory, verbose=False, max_iterations=3):
    # query to get_tools can be used to be embedded and relevant tools found
    # see here: https://langchain-langchain.vercel.app/docs/use_cases/agents/custom_agent_with_plugin_retrieval#tool-retriever

    # we only use one tool for now, but this is highly extensible!
    order_ticket_agent = OrderTicketAgent.init(llm=llm,
                                               memory=memory, verbose=verbose, max_iterations=max_iterations)
    tools = [
        Tool(
            name="OrderSupportTicket",
            func=order_ticket_agent.run,
            return_direct=True,
            description="useful for when you need to create a support ticket for an issue a customer has raised about their order"

        )


    ]

    return tools
