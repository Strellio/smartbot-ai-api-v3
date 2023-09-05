from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Redis, MongoDBAtlasVectorSearch
from app.lib.db import atlasClient
from langchain.tools import Tool


from app.constant import ORDER_VECTORSTORE_COLLECTION_NAME, ORDER_VECTORSTORE_INDEX_NAME


def getOrderKnowlegeBase(llm: ChatOpenAI, business, verbose=False, ):

    db_name = business.get('account_name')
    collection = atlasClient[db_name][ORDER_VECTORSTORE_COLLECTION_NAME]

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=OpenAIEmbeddings(),
        index_name=ORDER_VECTORSTORE_INDEX_NAME
    )

    order_doc_retriever = vectorstore.as_retriever()
    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=order_doc_retriever, verbose=verbose
    )

    return knowledge_base


def getTools(llm: ChatOpenAI, memory, business, customer, chat_platform, user_input, verbose=False, max_iterations=10):
    knowledge_base = getOrderKnowlegeBase(
        llm=llm, business=business, verbose=verbose)
    tools = [
        Tool(
            name="OrderSearch",
            func=knowledge_base.run,
            return_direct=False,
            description="useful for when you need to answer questions about order information"
            # description="useful for when you need to answer questions about order information, getting status and update for orders",
        )
    ]

    return tools
