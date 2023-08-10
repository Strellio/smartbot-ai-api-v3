from os import getenv
from langchain.agents import load_tools, Tool
from langchain.chat_models import ChatOpenAI
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS

from langchain.embeddings import OpenAIEmbeddings


from langchain.vectorstores import Redis, MongoDBAtlasVectorSearch

from langchain.vectorstores import mongodb_atlas
from pymongo import MongoClient


from app.agents.tickets.create.agent import OrderTicketAgent
from app.loaders.shopify import ShopifyLoader


# initialize MongoDB python client
client = MongoClient(
    "mongodb+srv://wisdom:bp000063@cluster0.pxsne.mongodb.net/?retryWrites=true&w=majority")

db_name = "smart-store-wis"
collection_name = "products-store"
collection = client[db_name][collection_name]
index_name = "products-retriever"


def setupProductKnowlegeBase(llm: ChatOpenAI, business, verbose=False, ):
    shpify_loader = ShopifyLoader(domain=business.get("shop").get("external_platform_domain"),
                                  access_token=business.get("shop").get("external_access_token"), resource="products")

    # index = VectorstoreIndexCreator(
    #     vectorstore_cls=Redis, vectorstore_kwargs={"index_name": "store-products", "redis_url": f"{getenv('REDIS_URL')}"}).from_loaders([shpify_loader])

    # index = VectorstoreIndexCreator(
    #     vectorstore_cls=MongoDBAtlasVectorSearch, vectorstore_kwargs={"index_name": index_name, "collection": collection}).from_loaders([shpify_loader])

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=OpenAIEmbeddings(),
        index_name=index_name
    )

    stripe_doc_retriever = vectorstore.as_retriever()
    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=stripe_doc_retriever, verbose=verbose
    )

    return knowledge_base


def getTools(llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=3):
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
