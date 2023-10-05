
import re
import os
from app.agents.assistant.agent import ShopAssistant
from app.agents.team_selection.chain import SubTeamAnalyzerChain


from app.models import Input
from app.services.businesses import getBusinessAndChatPlatform
from app.services.customers.get_customer import getCustomerByPlatform
from app.utils.llm import getLLM
from app.utils.memory import getMemory


def remove_tags(text_with_tags):
    # Remove lines containing "Tags:"
    text_without_tags = re.sub(r'\n\s*-?\s*Tags:.*\n', '\n', text_with_tags)
    return text_without_tags.strip()


def markdown_to_text(markdown_string):
    # Remove Markdown link syntax and keep only the URLs
    markdown_string = re.sub(r'\[.*?\]\((.*?)\)', r'\1', markdown_string)

    # Remove Markdown emphasis and bold syntax
    markdown_string = re.sub(r'\*{1,2}', '', markdown_string)

    return markdown_string.strip()


def format_response(response: str):
    response_without_tags = remove_tags(response)
    md_to_text = markdown_to_text(response_without_tags)
    return md_to_text.replace("AI:", "").replace("Assistant:", "")


def conversation(input: Input):
    try:
        input.message = input.message.replace("AI:", "").replace(
            "Assistant:", "").replace("Customer:", "")
        llm = getLLM()
        business, chat_platform = getBusinessAndChatPlatform(input.metadata)
        customer = getCustomerByPlatform(
            input.sender, chat_platform.get("platform"))
        message_memory = getMemory(session_id=input.sender, db_name=business.get("account_name"),
                                   memory_key="chat_history")
        routing_memory = getMemory(session_id=input.sender, db_name=business.get("account_name"),
                                   memory_key="chat_history", collection_name="chat_routing_history")
        sub_team_analyzer_chain = SubTeamAnalyzerChain.from_llm(
            llm=getLLM(model_name='gpt-4'), verbose=os.environ.get("VERBOSE"), memory=routing_memory)
        sub_team_id = sub_team_analyzer_chain.run(input=input.message)
        print(sub_team_id)
        shop_assistant = ShopAssistant.init(
            llm=llm, memory=message_memory, business=business, chat_platform=chat_platform, customer=customer, verbose=os.environ.get("VERBOSE"), user_input=input.message, sub_team_id=f"{sub_team_id}")
        # with PromptWatch(api_key=os.getenv("PROMPTWATCH_API_KEY")) as pw:
        output = shop_assistant.run(input=input.message)
        return format_response(output)
    except Exception as e:
        print(e)
        return "Sorry, I experienced an error trying to respond to you. I have notified my team about this. Please try again later."
