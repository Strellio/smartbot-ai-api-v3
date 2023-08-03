
from langchain.chat_models import ChatOpenAI
import os


def getLLM(model_name=os.environ.get("DEFAULT_MODEL_NAME"), temperature=0):
    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
