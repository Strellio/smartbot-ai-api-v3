from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory, MongoDBChatMessageHistory
import os


def getMemory(session_id: str, db_name: str, memory_key: str, collection_name="chat_message_history", return_messages=False):

    message_history = MongoDBChatMessageHistory(
        connection_string=os.environ.get("DATABASE_URL"), database_name=db_name, collection_name=collection_name, session_id=session_id
    )

    memory = ConversationBufferMemory(
        memory_key=memory_key, chat_memory=message_history, k=5, return_messages=return_messages, human_prefix="Customer"
    )
    return memory
