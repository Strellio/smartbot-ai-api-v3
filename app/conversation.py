
from app.agents.assistant.agent import ShopAssistant

from app.models import Input
from app.utils.memory import getMemory


def conversation(input: Input):
    memory = getMemory(session_id=input.sender,
                       memory_key="conversation_history")
    shop = {"name": "Tiktoken", "url": "https://tiktoken.com"}
    shop_assistant = ShopAssistant.init(memory=memory, shop=shop, verbose=True)
    output = shop_assistant.run(input=input.message)
    return output
