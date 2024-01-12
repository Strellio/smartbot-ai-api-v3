from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Redis, MongoDBAtlasVectorSearch

from langchain.text_splitter import CharacterTextSplitter

from langchain.vectorstores import FAISS
from app.agents.order.track.agent import OrderTrackAgent


from app.lib.db import atlasClient

from app.agents.human_hand_off.agent import HumanHandoffAgent
from app.agents.human_hand_off.tools import HumanHandoffTool


from app.agents.tickets.create.agent import OrderTicketAgent


from app.agents.tickets.status.agent import TicketStatusAgent
from app.constant import KNOWLEDGE_BASE_VECTORSTORE_COLLECTION_NAME, KNOWLEDGE_BASE_VECTORSTORE_INDEX_NAME

from app.services.agents.get_business_agents import getBusinessOnlineAgent
from app.utils.memory import getMemory


def getHumanHandOffTool(llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=10, user_input=''):

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
            max_iterations=max_iterations,
            user_input=user_input
        )
        return Tool(
            name="HandOffConversationToHuman",
            func=human_handoff_agent.run,
            return_direct=True,
            description="useful for when you need to hand off the conversation to a human and let the customer talk to a human"
        )


def getKnowlegeBase(llm: ChatOpenAI, business, customer, verbose=False, **kwargs):
    db_name = business.get('account_name')
    collection = atlasClient[db_name][KNOWLEDGE_BASE_VECTORSTORE_COLLECTION_NAME]

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=OpenAIEmbeddings(),
        index_name=KNOWLEDGE_BASE_VECTORSTORE_INDEX_NAME
    )

    order_doc_retriever = vectorstore.as_retriever()
    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=order_doc_retriever, verbose=verbose
    )

    return knowledge_base
