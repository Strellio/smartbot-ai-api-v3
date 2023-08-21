
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

    def __init__(self, customer: Any,  business: Any, chat_platform: Any) -> None:
        super().__init__(customer=customer, business=business, chat_platform=chat_platform)
        self.customer = customer
        self.business = business
        self.chat_platform = chat_platform

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        print("llm_output handoff", llm_output)

        return AgentFinish(
            {
                "output": llm_output
            },
            llm_output,
        )
