from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Redis, MongoDBAtlasVectorSearch
from app.lib.db import atlasClient
from langchain.tools import Tool


from app.constant import ORDER_VECTORSTORE_COLLECTION_NAME, ORDER_VECTORSTORE_INDEX_NAME, PRODUCT_VECTORSTORE_COLLECTION_NAME, PRODUCT_VECTORSTORE_INDEX_NAME
from app.utils.memory import getMemory


def getProductKnowlegeBase(llm: ChatOpenAI, business, customer, verbose=False,  **kwargs):

    # get data and saving. botth redis and mongodb
    # shpify_loader = ShopifyLoader(domain=business.get("shop").get("external_platform_domain"),
    #                               access_token=business.get("shop").get("external_access_token"), resource="products")

    # index = VectorstoreIndexCreator(
    #     vectorstore_cls=Redis, vectorstore_kwargs={"index_name": "store-products", "redis_url": f"{getenv('REDIS_URL')}"}).from_loaders([shpify_loader])

    # index = VectorstoreIndexCreator(
    #     vectorstore_cls=MongoDBAtlasVectorSearch, vectorstore_kwargs={"index_name": index_name, "collection": collection}).from_loaders([shpify_loader])

    db_name = business.get('account_name')
    collection = atlasClient[db_name][PRODUCT_VECTORSTORE_COLLECTION_NAME]

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=OpenAIEmbeddings(),
        index_name=PRODUCT_VECTORSTORE_INDEX_NAME
    )

    product_doc_retriever = vectorstore.as_retriever()
    knowledge_base = ConversationalRetrievalChain.from_llm(
        llm=llm, chain_type="stuff", retriever=product_doc_retriever, verbose=verbose, memory=getMemory(session_id=customer.get("_id"), db_name=business.get("account_name"),
                                                                                                        memory_key="chat_history", return_messages=True)
    )

    return knowledge_base


def getTools(llm: ChatOpenAI, memory, business, customer, verbose=False, max_iterations=10, **kwargs):
    knowledge_base = getProductKnowlegeBase(
        llm=llm, business=business, customer=customer,  verbose=verbose)
    tools = [
        Tool(
            name="ProductSearch",
            func=knowledge_base.run,
            return_direct=False,
            description="Searches and returns documents regarding the products we sell. The input to tool must always be a string or json string"
            # description="useful for when you need to answer questions about order information, getting status and update for orders",
        )
    ]

    return tools
