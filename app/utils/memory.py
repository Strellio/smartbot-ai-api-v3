from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
import os


def getMemory(session_id: str, memory_key: str):
    print(os.environ.get("REDIS_URL"))
    message_history = RedisChatMessageHistory(
        url=os.environ.get("REDIS_URL"), ttl=600, session_id=session_id
    )

    memory = ConversationBufferMemory(
        memory_key=memory_key, message_history=message_history, k=5, return_messages=True
    )
    return memory
