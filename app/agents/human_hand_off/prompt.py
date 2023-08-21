
from app.template.custom_template import PromptTemplateWithTools
from app.agents.tickets.create.tools import support_ticket_tools

human_handoff_template = """
You are an AI assistant and you are responsible for helping handing off conversation to live agent if requested by the customer.

There is live agent available online now.


Do not generate any hypothetical conversation and you must act as an assistant only.


After analyzing all the 4 scenarios, respond to the customer in the format:handoff: your response here.

Chat history:
{chat_history}
Customer: {input}


agent scratchpad:
{agent_scratchpad}

"""


human_handoff_prompt = PromptTemplateWithTools(
    template=human_handoff_template,
    tools_getter=lambda x: [],
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=[
        "input",
        "chat_history",
        "intermediate_steps"

    ],
)
