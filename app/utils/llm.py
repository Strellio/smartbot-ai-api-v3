
from langchain.chat_models import ChatOpenAI
import os

DEFAULT_MODEL_NAME = os.environ.get("DEFAULT_MODEL_NAME")


def getLLM(model_name='gpt-3.5-turbo', temperature=0):
    print("model_name", model_name)
    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    return llm
