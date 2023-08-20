from typing import Optional, Type
from pydantic import BaseModel
from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


class HumanHandoffToolInput(BaseModel):
    question: Optional[str] = None


class HumanHandoffTool(BaseTool):
    name = "HumanHandoff"
    description = "useful for when you need to handoff the conversation to a human and let the customer talk to a human"
    args_schema: Type[BaseModel] = HumanHandoffToolInput
    return_direct = True

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return "There are currently no live agent available at the moment. Will you still want me to proceed handoff the conversation?"

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")


handoff_tools = [
    HumanHandoffTool()
]


hand_off_tools_names = [tool.name for tool in handoff_tools]
