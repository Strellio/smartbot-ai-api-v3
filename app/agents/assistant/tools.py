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


from app.agents.tickets.create.agent import OrderTicketAgent


from app.agents.tickets.status.agent import TicketStatusAgent

from app.loaders.shopify import ShopifyLoader

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


# initialize MongoDB python client
client = MongoClient(getenv("MONGODB_ATLAS_URL"))

db_name = "smart-store-wis"
collection_name = "products-store"
collection = client[db_name][collection_name]
index_name = "products-retriever"


class HumanHandoffToolInput(BaseModel):
    question: Optional[str] = None


class HumanHandoffTool(BaseTool):
    name = "HumanHandoff"
    description = "useful for when you need to handoff the conversation to a human and let the customer talk to a human"
    args_schema: Type[BaseModel] = HumanHandoffToolInput
    # return_direct = True

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return "You can now to one of our live agents as you have requested."

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")


def setupProductKnowlegeBase(llm: ChatOpenAI, business, verbose=False, ):
    # shpify_loader = ShopifyLoader(domain=business.get("shop").get("external_platform_domain"),
    #                               access_token=business.get("shop").get("external_access_token"), resource="products")

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

    ticket_status_agent = TicketStatusAgent.init(llm=llm,
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
            name="CreateNewSupportTicket",
            func=order_ticket_agent.run,
            return_direct=True,
            description="useful for when you need to create a support ticket for an issue a customer has raised about their order. This is when a customer report an issue to you"

        ),
        Tool(
            name="CheckStatusOfCreatedSupportTicket",
            func=ticket_status_agent.run,
            return_direct=True,
            description="useful for when you need to check the status of a support ticket or follow up to get the status of the support ticket. This is when a customer ask you about the status of a ticket or an update about an issue they have already reported"

        ),
        HumanHandoffTool(),





    ]

    return tools
