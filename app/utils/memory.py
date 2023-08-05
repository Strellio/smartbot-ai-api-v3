from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
import os


def getMemory(session_id: str, memory_key: str):
    message_history = RedisChatMessageHistory(
        url=f"{os.environ.get('REDIS_URL')}/2", ttl=600, session_id=session_id
    )

    memory = ConversationBufferMemory(
        memory_key=memory_key, chat_memory=message_history, k=5, return_messages=True, human_prefix="Customer"
    )
    return memory
