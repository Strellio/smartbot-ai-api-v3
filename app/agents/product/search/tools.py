from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Redis, MongoDBAtlasVectorSearch
from app.lib.db import atlasClient
from langchain.tools import Tool, StructuredTool

from langchain.agents.agent_toolkits import create_retriever_tool


from app.constant import PRODUCT_VECTORSTORE_COLLECTION_NAME, PRODUCT_VECTORSTORE_INDEX_NAME
from app.utils.memory import getMemory


def getProductKnowlegeBase(llm: ChatOpenAI, business, customer, verbose=False,  **kwargs):

    print(business.get('account_name'),  PRODUCT_VECTORSTORE_COLLECTION_NAME,
          PRODUCT_VECTORSTORE_INDEX_NAME)

    db_name = business.get('account_name')
    collection = atlasClient[db_name][PRODUCT_VECTORSTORE_COLLECTION_NAME]

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=OpenAIEmbeddings(),
        index_name=PRODUCT_VECTORSTORE_INDEX_NAME
    )

    product_doc_retriever = vectorstore.as_retriever()

    knowledge_base = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=product_doc_retriever, verbose=verbose
    )

    def parsing_multiplier(input):
        if type(input) is list:
            return knowledge_base.run(f"{''.join(input)}. Make sure you return the full information about the product")
        else:
            print("input is not a list", input)
            return knowledge_base.run(f"{input}. Make sure you return the full information about the product")

    return parsing_multiplier


def getTools(llm: ChatOpenAI, memory, business, customer, verbose=False, max_iterations=10, **kwargs):
    knowledge_base = getProductKnowlegeBase(
        llm=llm, business=business, customer=customer,  verbose=verbose)
    tools = [
        StructuredTool.from_function(
            name="ProductSearch",
            func=knowledge_base,
            return_direct=False,
            description="useful for when you need to answer questions about product information."
        )
    ]

    return tools
