from os import getenv
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


def setupProductKnowlegeBase(llm: ChatOpenAI, business, verbose=False, ):
    shpify_loader = ShopifyLoader(domain=business.get("shop").get("external_platform_domain"),
                                  access_token=business.get("shop").get("external_access_token"), resource="products")

    index = VectorstoreIndexCreator(
        vectorstore_cls=Redis, vectorstore_kwargs={"index_name": "products", "redis_url": f"{getenv('REDIS_URL')}/3"}).from_loaders([shpify_loader])

    stripe_doc_retriever = index.vectorstore.as_retriever()
    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=stripe_doc_retriever, verbose=verbose
    )

    return knowledge_base


def getTools(llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=3):
    # query to get_tools can be used to be embedded and relevant tools found
    # see here: https://langchain-langchain.vercel.app/docs/use_cases/agents/custom_agent_with_plugin_retrieval#tool-retriever

    # we only use one tool for now, but this is highly extensible!
    order_ticket_agent = OrderTicketAgent.init(llm=llm,
                                               memory=memory, verbose=verbose, business=business, chat_platform=chat_platform, customer=customer, max_iterations=max_iterations)
    knowledge_base = setupProductKnowlegeBase(
        llm=llm, verbose=verbose, business=business)

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
            # return_direct=True,
            description="useful for when you need to create a support ticket for an issue a customer has raised about their order"

        )


    ]

    return tools
