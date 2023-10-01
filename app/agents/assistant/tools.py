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
from app.constant import PRODUCT_VECTORSTORE_COLLECTION_NAME, PRODUCT_VECTORSTORE_INDEX_NAME

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


def getOffersAndPromos(llm: ChatOpenAI, business, customer, verbose=False, **kwargs):
    text = """
            Amazing Offers, Discounts, Promotions, and Coupons!

            Dear Valued Customers,

            We are thrilled to present to you our latest collection of irresistible offers, discounts, promotions, and coupons. As a token of our appreciation for your continued support, we want to ensure you have access to the best deals on our premium products.

            Here's what's in store for you:

            1. Seasonal Discount Extravaganza:
            Get ready for a shopping spree like no other! Enjoy up to 50% off on selected items from our newest arrivals and classic collections. Whether it's fashion, accessories, or home decor, there's something for everyone. This offer is valid until [expiration date].

            2. Bundle and Save:
            Upgrade your style with our bundle deals. Buy two items from the same category and get 30% off on the third item. Mix and match to create your perfect look. Hurry, this offer ends on [expiration date].

            3. Exclusive Email Coupons:
            Subscribe to our newsletter and unlock a world of exclusive deals. Receive special coupons directly in your inbox that can be used for extra discounts on your favorite products. Don't miss out on this limited-time opportunity!

            4. Loyalty Rewards Program:
            Our loyal customers mean the world to us. With our Loyalty Rewards Program, every purchase you make earns you points that can be redeemed for future discounts. The more you shop, the more you save!

            5. Flash Sales Galore:
            Stay tuned to our website and social media channels for surprise flash sales. These limited-time offers are the perfect chance to grab your desired products at unbeatable prices. Keep your eyes peeled!

            6. Refer a Friend, Get Rewarded:
            Share the joy of shopping with your friends and family. Refer someone to us, and when they make their first purchase, you both receive a special discount. Spread the love and the savings!

            7. Special Occasion Discounts:
            Celebrate birthdays, anniversaries, and holidays with us! Enjoy exclusive discounts during special occasions to make your moments even more memorable.

        """

    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )

    documents = text_splitter.create_documents([text])

    vectorestore = FAISS.from_documents(
        documents=documents, embedding=OpenAIEmbeddings())
    offers_knowledge_base = ConversationalRetrievalChain.from_llm(
        llm=llm, chain_type="stuff", retriever=vectorestore.as_retriever(), memory=getMemory(session_id=customer.get("_id"), db_name=business.get("account_name"),
                                                                                             memory_key="chat_history", return_messages=True)
    )

    return offers_knowledge_base
