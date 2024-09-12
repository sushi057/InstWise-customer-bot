import os
from langchain_openai import ChatOpenAI


def get_openai_model():
    model = ChatOpenAI(
        model="gpt-4o", temperature=0.5, api_key=os.getenv("OPENAI_API_KEY")
    )
    return model
