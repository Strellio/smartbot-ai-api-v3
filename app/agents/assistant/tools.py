from os import getenv
from typing import Optional, Type
from pydantic import BaseModel
from langchain.tools import BaseTool, Tool
from langchain.chat_models import ChatOpenAI
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Redis, MongoDBAtlasVectorSearch

from langchain.vectorstores import mongodb_atlas
from pymongo import MongoClient
from app.agents.human_hand_off.agent import HumanHandoffAgent
from app.agents.human_hand_off.tools import HumanHandoffTool


from app.agents.tickets.create.agent import OrderTicketAgent


from app.agents.tickets.status.agent import TicketStatusAgent
from app.constant import PRODUCT_VECTORSTORE_COLLECTION_NAME, PRODUCT_VECTORSTORE_INDEX_NAME

from app.services.agents.get_business_agents import getBusinessOnlineAgent


# initialize MongoDB python client
client = MongoClient(getenv("MONGODB_ATLAS_URL"))


def getHumanHandOffTool(llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=3):

    onlineAgent = getBusinessOnlineAgent(businessId=business.get("_id"))

    if onlineAgent is not None:
        return HumanHandoffTool(customer=customer)
    else:
        human_handoff_agent = HumanHandoffAgent.init(
            llm=llm,
            memory=memory,
            verbose=verbose,
            business=business,
            chat_platform=chat_platform,
            customer=customer,
            max_iterations=max_iterations
        )
        return Tool(
            name="HandOffConversationToHuman",
            func=human_handoff_agent.run,
            return_direct=True,
            description="useful for when you need to hand off the conversation to a human and let the customer talk to a human"
        )


def setupProductKnowlegeBase(llm: ChatOpenAI, business, verbose=False, ):

    # get data and saving. botth redis and mongodb
    # shpify_loader = ShopifyLoader(domain=business.get("shop").get("external_platform_domain"),
    #                               access_token=business.get("shop").get("external_access_token"), resource="products")

    # index = VectorstoreIndexCreator(
    #     vectorstore_cls=Redis, vectorstore_kwargs={"index_name": "store-products", "redis_url": f"{getenv('REDIS_URL')}"}).from_loaders([shpify_loader])

    # index = VectorstoreIndexCreator(
    #     vectorstore_cls=MongoDBAtlasVectorSearch, vectorstore_kwargs={"index_name": index_name, "collection": collection}).from_loaders([shpify_loader])

    db_name = business.get('business_name').replace(" ", "-")
    collection = client[db_name][PRODUCT_VECTORSTORE_COLLECTION_NAME]

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=OpenAIEmbeddings(),
        index_name=PRODUCT_VECTORSTORE_INDEX_NAME
    )

    product_doc_retriever = vectorstore.as_retriever()
    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=product_doc_retriever, verbose=verbose
    )

    return knowledge_base


def getTools(llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=3):
    order_ticket_agent = OrderTicketAgent.init(llm=llm,
                                               memory=memory, verbose=verbose, business=business, chat_platform=chat_platform, customer=customer, max_iterations=max_iterations)

    ticket_status_agent = TicketStatusAgent.init(llm=llm,
                                                 memory=memory, verbose=verbose, business=business, chat_platform=chat_platform, customer=customer, max_iterations=max_iterations)

    human_handoff_tool = getHumanHandOffTool(llm=llm,
                                             memory=memory, verbose=verbose, business=business, chat_platform=chat_platform, customer=customer, max_iterations=max_iterations)
    knowledge_base = setupProductKnowlegeBase(
        llm=llm, verbose=verbose, business=business)

    tools = [
        Tool(
            name="ProductSearch",
            func=knowledge_base.run,
            return_direct=True,
            description="useful for when you need to answer questions about product information",
        ),
        Tool(
            name="CreateNewSupportTicket",
            func=order_ticket_agent.run,
            return_direct=True,
            description="useful for when you need to create a support ticket for an issue a customer has raised about their order. This is when a customer report an issue to you."

        ),
        Tool(
            name="CheckStatusOfCreatedSupportTicket",
            func=ticket_status_agent.run,
            return_direct=True,
            description="useful for when you need to check the status of a support ticket or follow up to get the status of the support ticket. This is when a customer ask you about the status of a ticket or an update about an issue they have already reported"

        ),

        human_handoff_tool

    ]

    return tools
