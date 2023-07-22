from langchain.agents import initialize_agent, Tool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType
import os
import yaml
from langchain.agents.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain.requests import RequestsWrapper
from langchain.agents.agent_toolkits.openapi import planner
import tiktoken


def conversation(human_input):

    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True)

    with open("smartbot-openapi.spec.yaml") as f:
        raw_openai_api_spec = yaml.load(f, Loader=yaml.Loader)
    openai_api_spec = reduce_openapi_spec(raw_openai_api_spec)

    requests_wrapper = RequestsWrapper()

    endpoints = [
        (route, operation)
        for route, operations in raw_openai_api_spec["paths"].items()
        for operation in operations
        if operation in ["get", "post"]
    ]

    enc = tiktoken.encoding_for_model("text-davinci-003")

    def count_tokens(s):
        return len(enc.encode(s))

    count_tokens(yaml.dump(raw_openai_api_spec))

    template = """
    As a retail shopping assistant, your priority is to report our customer complaints to us as a ticket. you need to retrieve all the necessary information to be able to create the issue ticket. 

    Order ID and Customer ID must be part of the information you ask from the user if the issue is about an order.

    If the API endpoint you want to use is not part of the documentation you can skip it. It is okay

    Now, let's get started and assist our customers with any issues they might have!

    Customer: {query}
    Assistant:



    """

    prompt = PromptTemplate(
        input_variables=["query"],
        template=template
    )

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    api_agent = planner.create_openapi_agent(
        openai_api_spec, requests_wrapper, llm)

    # initialize the LLM tool
    llm_tool = Tool(
        name='Order issues',
        func=llm_chain.run,
        description='use this tool for customer report issues with their order'
    )

    api_tool = Tool.from_function(
        name='Ticket Creation',
        func=api_agent.run,
        description='use this tool to create a ticket on behalf of the customer'
    )

    tools = [api_tool, llm_tool]

    conversational_agent = initialize_agent(
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        tools=tools,
        llm=llm,
        verbose=True,
        max_iterations=3,
        memory=memory,
        handle_parsing_errors=True,
    )

    result = conversational_agent.run(
        human_input
    )
    return result
