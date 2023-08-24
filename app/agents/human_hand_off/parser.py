
import os
import re
import pandas as pd
from typing import Any, Union
from langchain.agents.agent import AgentOutputParser, OutputParserException
from langchain.schema import AgentAction, AgentFinish
from pydantic import BaseModel
from app.agents.tickets.create.utils import generateTicketPayload
from app.services.tickets.create_ticket import createTicket

import requests
import json


class HumanHandOffOutputParser(AgentOutputParser):
    customer: Any
    business: Any
    chat_platform: Any
    ai_prefix: str = "Assistant"  # change for salesperson_name

    def __init__(self, customer: Any,  business: Any, chat_platform: Any) -> None:
        super().__init__(customer=customer, business=business, chat_platform=chat_platform)
        self.customer = customer
        self.business = business
        self.chat_platform = chat_platform

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        print("llm_output handoff", llm_output)
        if f"{self.ai_prefix}:" in llm_output:
            return AgentFinish(
                {"output": llm_output.split(
                    f"{self.ai_prefix}:")[-1].strip()}, llm_output
            )

        regex = r"(.*?)\nAction:(.*?)\nAction Input: (.*)"
        match = re.search(regex, llm_output)
        if not match:
            print("no match")
            # TODO - this is not entirely reliable, sometimes results in an error.
            return AgentFinish(
                {
                    "output":   "I apologize, I was unable to find the answer to your question. Is there anything else I can help with?"
                },
                llm_output,
            )
            # raise OutputParserException(f"Could not parse LLM output: `{text}`")

        action = match.group(2)
        action_input = match.group(3)
        return AgentAction(action.strip(), action_input.strip(" ").strip('"'), llm_output)
