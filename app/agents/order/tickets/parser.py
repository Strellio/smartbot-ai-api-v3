
import os
import re
import pandas as pd
from typing import Union
from langchain.agents.agent import AgentOutputParser, OutputParserException
from langchain.schema import AgentAction, AgentFinish

import requests
import json


class SupportTicketOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        print("llm_output", llm_output)
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
        print("action", action_input)
        # payload = json.loads(action_input)
        # r = requests.post(payload["url"], payload["data"])
        return AgentFinish(
            # Return values is generally always a dictionary with a single `output` key
            # It is not recommended to try anything else at the moment :)
            return_values={"output": llm_output},
            log=llm_output,
        )
        # Return the action and action input
        # return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
