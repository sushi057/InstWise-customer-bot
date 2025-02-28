from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

load_dotenv()


def init_model(
    fully_specified_name: str,
    *,
    temperature: float | None = 0.5,
) -> BaseChatModel:
    """Initialize the configured chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name

    return init_chat_model(model, model_provider=provider, temperature=temperature)


if __name__ == "__main__":
    llm = init_model(fully_specified_name="gpt-4o-mini")
    print(llm.invoke("What is the capital of France?"))
