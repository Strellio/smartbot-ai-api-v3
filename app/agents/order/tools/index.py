from langchain.agents import load_tools


requests_tools = load_tools(["requests_post"])

requests_tools[0].name = "create_support_ticket"

requests_tools[0].description = "useful when you wants to create a support ticket"


support_ticket_tools = requests_tools


# requests_tools = [CreateSupportTicketTool()]


support_ticket_tools_names = [tool.name for tool in support_ticket_tools]
