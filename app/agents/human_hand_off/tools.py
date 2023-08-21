from typing import Optional, Type, Any
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from app.services.agents.talk_to_agent import talkToAgent


class HumanHandoffToolInput(BaseModel):
    question: Optional[str] = None


class HumanHandoffTool(BaseTool, BaseModel):
    name = "HumanHandoff"
    description = "useful for when you need to handoff the conversation to a human and let the customer talk to a human"
    args_schema: Type[BaseModel] = HumanHandoffToolInput
    return_direct = True
    customer: Any

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        talkToAgent(customerId=self.customer.get("_id"))
        return "I have now handed off the conversation to one of our live agents. I will now keep quiet till the live agent handoff the conversation back to me"

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")
