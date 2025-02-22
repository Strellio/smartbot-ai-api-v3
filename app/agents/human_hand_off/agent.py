
from typing import Any
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from pydantic import Field, BaseModel
from langchain.agents import LLMSingleActionAgent, AgentExecutor
from app.agents.human_hand_off.parser import HumanHandOffOutputParser
from app.agents.human_hand_off.prompt import human_handoff_prompt
from app.agents.human_hand_off.tools import HumanHandoffTool


class HumanHandoffAgent(BaseModel):
    human_handoff_agent: Any = Field(...)
    llm_chain: Any = Field(...)
    user_input: str

    @classmethod
    def init(self, llm: ChatOpenAI, memory, business, customer, chat_platform, verbose=False, max_iterations=10, user_input='') -> "HumanHandoffAgent":
        handoff_tools = [
            HumanHandoffTool(
                customer=customer
            )
        ]
        hand_off_tools_names = [tool.name for tool in handoff_tools]

        llm_chain = LLMChain(
            llm=llm, prompt=human_handoff_prompt)

        human_handoff_action_with_tools = LLMSingleActionAgent(
            output_parser=HumanHandOffOutputParser(
                business=business, customer=customer, chat_platform=chat_platform),
            llm_chain=llm_chain,
            stop=["\nObservation:"],
            allowed_tools=hand_off_tools_names,
            verbose=verbose,

            max_iterations=max_iterations,
        )

        human_handoff_agent = AgentExecutor.from_agent_and_tools(
            agent=human_handoff_action_with_tools, tools=handoff_tools, verbose=verbose, max_iterations=max_iterations, memory=memory

        )

        return self(human_handoff_agent=human_handoff_agent, llm_chain=llm_chain, user_input=user_input)

    def run(self, input: str):
        return self.human_handoff_agent.run(self.user_input)
