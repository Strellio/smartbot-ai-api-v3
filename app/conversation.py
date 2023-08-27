
import os
from app.agents.assistant.agent import ShopAssistant


from app.models import Input
from app.services.businesses import getBusinessAndChatPlatform
from app.services.customers.get_customer import getCustomerByPlatform
from app.utils.llm import getLLM
from app.utils.memory import getMemory


def conversation(input: Input):
    llm = getLLM()
    memory = getMemory(session_id=input.sender,
                       memory_key="chat_history")

    business, chat_platform = getBusinessAndChatPlatform(input.metadata)
    customer = getCustomerByPlatform(
        input.sender, chat_platform.get("platform"))

    shop_assistant = ShopAssistant.init(
        llm=llm, memory=memory, business=business, chat_platform=chat_platform, customer=customer, verbose=True, user_input=input.message)
    # with PromptWatch(api_key=os.getenv("PROMPTWATCH_API_KEY")) as pw:
    output = shop_assistant.run(input=input.message)
    return output
