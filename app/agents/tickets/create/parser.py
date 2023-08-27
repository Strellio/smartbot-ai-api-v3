
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


class SupportTicketOutputParser(AgentOutputParser):
    customer: Any
    business: Any
    chat_platform: Any

    def __init__(self, customer: Any,  business: Any, chat_platform: Any) -> None:
        super().__init__(customer=customer, business=business, chat_platform=chat_platform)
        self.customer = customer
        self.business = business
        self.chat_platform = chat_platform

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        print("llm_output", llm_output)

        if ("create_support_ticket" in llm_output):
            regex = r'create_support_ticket:(?:\s?)(\{.*\})'
            # regex = r'llm_output create_support_ticket:\s*({.*?})\s*(?:,|$)|llm_output create_support_ticket:({.*?})\s*(?:,|$)'

            match = re.search(regex, llm_output)
            payloadStr = match.group(1)

            payload = json.loads(payloadStr)

            ticketInfo = generateTicketPayload(order_id=payload.get(
                "orderID"), ticket_type=payload.get("type"), **payload)

            result = createTicket(customer_id=self.customer.get("_id"), business_id=self.business.get(
                "_id"), chat_platform_id=self.chat_platform.get("_id"), email=self.customer.get("email"), **ticketInfo)

            return AgentFinish(
                {
                    "output": f"I have created a support ticket for you. Our team will get in touch with you to resolve your {ticketInfo.get('title')} request"
                },
                llm_output,
            )

        # Check if agent should finish
        if "Assistant:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split(
                    "Assistant:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action:(.*?)[\n]*Action Input: (.*)"
        # regex =r"Order Support Ticket Action Input: (.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            print("no match ticket")
            return AgentFinish(
                {
                    "output": llm_output
                },
                llm_output,
            )

            # raise OutputParserException(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        print("action", action)
        print("action_input", action_input)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
