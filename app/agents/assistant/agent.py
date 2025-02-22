

from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Any
from langchain.memory import ConversationBufferMemory
from app.agents.assistant.tools import getHumanHandOffTool, getKnowlegeBase
from app.agents.introduction.chain import IntroductionChain
from app.agents.knowlege_base.agent import KnowledgeBaseAgent


from app.agents.order.track.agent import OrderTrackAgent
from app.agents.product.search.agent import ProductKnowledgeBaseAgent

from app.agents.tickets.create.agent import OrderTicketAgent


from app.agents.tickets.status.agent import TicketStatusAgent


class ShopAssistant(BaseModel):
    shop_assistant_executor: Any = Field(...)

    @classmethod
    def init(self, llm: ChatOpenAI, memory: ConversationBufferMemory, business, chat_platform, customer, sub_team_id, verbose=False, max_iterations=10, user_input=''):

        sub_team_agent_dict = {
            "1": IntroductionChain.from_llm,
            "2": ProductKnowledgeBaseAgent.init,
            "3": OrderTicketAgent.init,
            "4": TicketStatusAgent.init,
            "5": OrderTrackAgent.init,
            "6": getHumanHandOffTool,
            "7": KnowledgeBaseAgent.init
        }

        handler = sub_team_agent_dict.get(sub_team_id)
        shop_assistant_executor = handler(llm=llm,
                                          memory=memory, verbose=verbose, business=business, chat_platform=chat_platform, customer=customer, max_iterations=max_iterations, user_input=user_input)

        return self(shop_assistant_executor=shop_assistant_executor)

    def run(self, input):
        ouput = self.shop_assistant_executor.run(input)
        return ouput
