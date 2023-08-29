from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory, MongoDBChatMessageHistory
import os


def getMemory(session_id: str, db_name: str, memory_key: str):
    # message_history = RedisChatMessageHistory(
    #     url=f"{os.environ.get('REDIS_URL')}/2", ttl=600, session_id=session_id
    # )

    message_history = MongoDBChatMessageHistory(
        connection_string=os.environ.get("DATABASE_URL"), database_name=db_name, collection_name="chat_message_history", session_id=session_id
    )

    memory = ConversationBufferMemory(
        memory_key=memory_key, chat_memory=message_history, k=15, return_messages=False, human_prefix="Customer"
    )
    return memory
