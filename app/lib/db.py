from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
load_dotenv()
client = MongoClient(getenv("DATABASE_URL"))
name = getenv("DATABASE_NAME")
db = client[name]

businessModel = db.businesses
chatPlatformModel = db.chat_platforms
sessionModel = db.sessions
agentsModel = db.agents
customerModel = db.customers
ticketModel = db.tickets
