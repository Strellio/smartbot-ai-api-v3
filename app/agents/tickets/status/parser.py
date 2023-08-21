
import re
import pandas as pd
from typing import Any, Union
from langchain.agents.agent import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish


class SupportTicketStatusOutputParser(AgentOutputParser):
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

        if ("support_ticket_status" in llm_output):
            regex = r'support_ticket_status:(.*)'
            match = re.search(regex, llm_output)
            ticketNumber = match.group(1)
            print("\n")
            print("ticketNumber", ticketNumber)

            return AgentFinish(
                {
                    "output": f"Your support ticket with number {ticketNumber} is in progress."
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
