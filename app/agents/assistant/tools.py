from langchain.agents import load_tools, Tool
from langchain.chat_models import ChatOpenAI
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS

from langchain.embeddings import OpenAIEmbeddings


from langchain.vectorstores.redis import Redis
from langchain.vectorstores import mongodb_atlas


from app.agents.order.tickets.agent import OrderTicketAgent
from app.loaders.shopify import ShopifyLoader


def setupProductKnowlegeBase(llm: ChatOpenAI, verbose=False, max_iterations=3):
    shpify_loader = ShopifyLoader(domain="https://smart-store-wis.myshopify.com",
                                  access_token="shpua_0b2ba5fa999251310ae908280c4ea62e", resource="products")

    redis_host = "localhost"
    redis_port = 6379

    index = VectorstoreIndexCreator(
        vectorstore_cls=Redis, vectorstore_kwargs={"index_name": "products", "redis_url": f"redis://{redis_host}:{redis_port}/3"}).from_loaders([shpify_loader])

    stripe_doc_retriever = index.vectorstore.as_retriever()
    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=stripe_doc_retriever, verbose=verbose
    )

    return knowledge_base


def getTools(llm: ChatOpenAI, memory, verbose=False, max_iterations=3):
    # query to get_tools can be used to be embedded and relevant tools found
    # see here: https://langchain-langchain.vercel.app/docs/use_cases/agents/custom_agent_with_plugin_retrieval#tool-retriever

    # we only use one tool for now, but this is highly extensible!
    order_ticket_agent = OrderTicketAgent.init(llm=llm,
                                               memory=memory, verbose=verbose, max_iterations=max_iterations)
    knowledge_base = setupProductKnowlegeBase(
        llm=llm, verbose=verbose, max_iterations=max_iterations)

    tools = [
        Tool(
            name="ProductSearch",
            func=knowledge_base.run,
            # return_direct=True,
            description="useful for when you need to answer questions about product information",
        ),
        Tool(
            name="OrderSupportTicket",
            func=order_ticket_agent.run,
            return_direct=True,
            description="useful for when you need to create a support ticket for an issue a customer has raised about their order"

        )


    ]

    return tools
