import os
from langchain_openai import ChatOpenAI


def get_openai_model(temperature: float = 0.5):
    model = ChatOpenAI(
        model="gpt-4o", temperature=temperature, api_key=os.getenv("OPENAI_API_KEY")
    )
    return model
