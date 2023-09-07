
import re
from typing import Union
from langchain.agents.agent import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish
from langchain.agents.conversational.prompt import FORMAT_INSTRUCTIONS


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
    return md_to_text


class ShopAssistantOutputParser(AgentOutputParser):
    ai_prefix: str = "Assistant"  # change for salesperson_name
    verbose: bool = False

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if self.verbose:
            print("TEXT")
            print(text)
            print("-------")
        if f"{self.ai_prefix}:" in text:
            response = format_response(text.split(
                f"{self.ai_prefix}:")[-1].strip())
            return AgentFinish(
                {"output": response}, text
            )
        regex = r"(.*?)\nAction:(.*?)\nAction Input: (.*)"
        match = re.search(regex, text)
        if not match:
            print("no match")
            # TODO - this is not entirely reliable, sometimes results in an error.
            return AgentFinish(
                {
                    "output":  "I apologize, I was unable to find the answer to your question. Can you reprase it or is there anything else I can help with?"
                },
                text,
            )
            # raise OutputParserException(f"Could not parse LLM output: `{text}`")

        action = match.group(2)
        action_input = match.group(3)
        return AgentAction(action.strip(), action_input.strip(" ").strip('"'), text)

    @property
    def _type(self) -> str:
        return "shop-assistant"
