
from app.agents.assistant.agent import ShopAssistant

from app.models import Input
from app.utils.llm import getLLM
from app.utils.memory import getMemory


def conversation(input: Input):
    llm = getLLM()
    memory = getMemory(session_id=input.sender,
                       memory_key="chat_history")
    shop = {"name": "Tiktoken", "url": "https://tiktoken.com"}

    print("input.message", input.message)

    shop_assistant = ShopAssistant.init(
        llm=llm, memory=memory, shop=shop, verbose=True)

    output = shop_assistant.run(input=input.message)
    return output
