import os
from typing import Literal
from langchain_openai import ChatOpenAI


def get_openai_model(
    model: Literal["gpt-4o", "gpt-4o-mini"] = "gpt-4o",
    temperature: float = "0.5",
):
    model = ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    return model
