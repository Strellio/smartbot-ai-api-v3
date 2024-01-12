from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Redis, MongoDBAtlasVectorSearch
from app.lib.db import atlasClient
from langchain.tools import Tool, StructuredTool


from app.constant import KNOWLEDGE_BASE_VECTORSTORE_COLLECTION_NAME, KNOWLEDGE_BASE_VECTORSTORE_INDEX_NAME


def getKnowlegeBase(llm: ChatOpenAI, business, verbose=False, **kwargs):
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

    def parsing_multiplier(input):
        print(input)
        if type(input) is list:
            return knowledge_base.run(f"{''.join(input)}")
        else:
            return knowledge_base.run(f"{input}")

    return parsing_multiplier


def getTools(llm: ChatOpenAI, memory, business, customer, chat_platform, user_input, verbose=False, max_iterations=10):
    knowledge_base = getKnowlegeBase(
        llm=llm, business=business, verbose=verbose)
    tools = [
        StructuredTool.from_function(
            name="StorePoliciesAndFAQs",
            func=knowledge_base,
            return_direct=False,
            description="useful for when you need to access some information about our store. it can be FAQ, store policies, contact information, promotions and discounts, etc",
            # description="useful for when you need to answer questions about order information, getting status and update for orders",
        )
    ]

    return tools
