from langchain.agents import initialize_agent, Tool, LLMSingleActionAgent
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType
import yaml
from langchain.agents.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain.requests import RequestsWrapper
from langchain.agents.agent_toolkits.openapi import planner
import tiktoken

from app.models import Input


def conversation(input: Input):

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
You are an AI assistant and the following is a conversation with customer. The assistant is helpful, creative, clever, and very friendly.

The assistant helps my customers book a flight and raise a support ticket.

When a  user wants to book a flight, below are the required fields the user must provide:

The user's name

The user's departure location

The user's destination location

The user's dates of travel

The user's budget for the trip

When a user wants to raise a support ticket, below are the required fields the user must provide:

The user's name

The order number

After collecting all these fields the Assistant should thank the human for their time. It should then write EODC (for end of data collection) and on a new line output all these fields as JSON.


Below  is your previous conversation with the customer:

{chat_history}

Human: {input}
    """

    prompt = PromptTemplate(
        input_variables=["input", "chat_history"],
        template=template
    )

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    llm_chain = ConversationChain(llm=llm, prompt=prompt, memory=memory)

    api_agent = planner.create_openapi_agent(
        openai_api_spec, requests_wrapper, llm)

    # initialize the LLM tool
    llm_tool = Tool(
        name='Flight Booking and Customer Support Ticket',
        func=llm_chain.run,
        description='use this tool for customers to book a flight and raise a support ticket'
    )

    api_tool = Tool.from_function(
        name='Ticket Creation',
        func=api_agent.run,
        description='use this tool to create a ticket on behalf of the customer'
    )

    tools = [llm_tool]

    print(prompt.format(input=input.message,
          chat_history=memory.load_memory_variables({})))

    conversational_agent = initialize_agent(
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        tools=tools,
        llm=llm,
        verbose=True,
        max_iterations=3,
        memory=memory,
        handle_parsing_errors=True,
        inpu
    )

    result = llm_chain.run(
        input.message
    )

    return result
