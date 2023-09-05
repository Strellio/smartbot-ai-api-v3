
import os
from app.agents.assistant.agent import ShopAssistant
from app.agents.team_selection.chain import SubTeamAnalyzerChain


from app.models import Input
from app.services.businesses import getBusinessAndChatPlatform
from app.services.customers.get_customer import getCustomerByPlatform
from app.utils.llm import getLLM
from app.utils.memory import getMemory


def conversation(input: Input):
    llm = getLLM()
    business, chat_platform = getBusinessAndChatPlatform(input.metadata)
    customer = getCustomerByPlatform(
        input.sender, chat_platform.get("platform"))
    message_memory = getMemory(session_id=input.sender, db_name=business.get("account_name"),
                               memory_key="chat_history")
    routing_memory = getMemory(session_id=input.sender, db_name=business.get("account_name"),
                               memory_key="chat_history", collection_name="chat_routing_history")
    sub_team_analyzer_chain = SubTeamAnalyzerChain.from_llm(
        llm, verbose=True, memory=routing_memory)
    sub_team_id = sub_team_analyzer_chain.run(input=input.message)
    print(sub_team_id)
    shop_assistant = ShopAssistant.init(
        llm=llm, memory=message_memory, business=business, chat_platform=chat_platform, customer=customer, verbose=True, user_input=input.message, sub_team_id=f"{sub_team_id}")
    # with PromptWatch(api_key=os.getenv("PROMPTWATCH_API_KEY")) as pw:
    output = shop_assistant.run(input=input.message)
    return output
