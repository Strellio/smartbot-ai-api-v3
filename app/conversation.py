
from app.agents.assistant.agent import ShopAssistant

from langchain.document_loaders import StripeLoader


from app.models import Input
from app.services.businesses import getBusinessAndChatPlatform
from app.utils.llm import getLLM
from app.utils.memory import getMemory


def conversation(input: Input):
    llm = getLLM()
    memory = getMemory(session_id=input.sender,
                       memory_key="chat_history")

    business, chatPlatform = getBusinessAndChatPlatform(input.metadata)

    shop_assistant = ShopAssistant.init(
        llm=llm, memory=memory, business=business, chatPlatform=chatPlatform, verbose=True)

    output = shop_assistant.run(input=input.message)
    return output
