import os
from typing import Literal
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def get_openai_model(
    model: Literal["gpt-4o", "gpt-4o-mini"] = "gpt-4o",
    temperature: float = 0.5,
) -> ChatOpenAI:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment.")
    else:
        model_instance = ChatOpenAI(
            model=model, temperature=temperature, api_key=SecretStr(openai_api_key)
        )
        return model_instance


if __name__ == "__main__":
    llm = get_openai_model(model="gpt-4o-mini")
    print(llm.invoke("What is the capital of France?"))
