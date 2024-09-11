import os
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)


def get_openai_model():
    model = ChatOpenAI(model="gpt-4o", temperature=0.5)
    return model
