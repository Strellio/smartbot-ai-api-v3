
import re
import pandas as pd
from typing import Union
from langchain.agents.agent import AgentOutputParser, OutputParserException
from langchain.schema import AgentAction, AgentFinish
from langchain.agents.conversational.prompt import FORMAT_INSTRUCTIONS


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
            return AgentFinish(
                {"output": text.split(f"{self.ai_prefix}:")[-1].strip()}, text
            )
        regex = r"(.*?)\nAction:(.*?)\nAction Input: (.*)"
        match = re.search(regex, text)
        if not match:
            print("no match")
            # TODO - this is not entirely reliable, sometimes results in an error.
            return AgentFinish(
                {
                    "output":   "I apologize, I was unable to find the answer to your question. Is there anything else I can help with?"
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
