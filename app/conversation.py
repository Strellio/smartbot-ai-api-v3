
from app.agents.assistant.agent import ShopAssistant

from app.models import Input
from app.utils.llm import getLLM
from app.utils.memory import getMemory


def conversation(input: Input):
    llm = getLLM()
    [memory, message_history] = getMemory(session_id=input.sender,
                                          memory_key="chat_history")
    shop = {"name": "Tiktoken", "url": "https://tiktoken.com"}

    shop_assistant = ShopAssistant.init(
        llm=llm, memory=memory, shop=shop, verbose=True)

    output = shop_assistant.run(input=input.message)
    return output
