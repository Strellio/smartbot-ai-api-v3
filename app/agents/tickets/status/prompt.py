
from app.template.custom_template import PromptTemplateWithTools
from app.agents.tickets.create.tools import support_ticket_tools

support_ticket_status_prompts = """
You are a assistant that assists customers to follow up on their support ticket to get update on it. 

The customer has to provide the ticketNumber in order for you to help identify the exact support ticket.

Always request for a new ticketNumber from the customer for every follow up.

Remember, do not generate any hypothetical conversations. You must have a real conversation with the customer.

Never tell the customer to contact the support team directly. 

Only after taking the ticketNumber from the customer return a response to the customer in the format: support_ticket_status:the ticketNumber taken from the customer.

You must respond according to the previous chat history
Do not respond to yourself and you must act as an Assistant only!

Chat history:
{chat_history}
Customer: {input}


agent scratchpad:
{agent_scratchpad}

"""


ticket_status_prompt = PromptTemplateWithTools(
    template=support_ticket_status_prompts,
    tools_getter=lambda x: [],
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=[
        "input",
        "chat_history",
        "intermediate_steps"

    ],
)
