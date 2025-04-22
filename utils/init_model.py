import logging
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

load_dotenv()

logger = logging.getLogger(__name__)


def init_model(
    fully_specified_name: str,
    *,
    temperature: float | None = 0.5,
    api_key: str | None = None,
) -> BaseChatModel:
    """Initialize the configured chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name

    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not provided in OrganizationDetail or .env")

    logger.info(
        f"Initializing chat model: provider={provider}, model={model}, temperature={temperature}, api_key={'***' if api_key else None}"
    )
    return init_chat_model(
        model,
        model_provider=provider,
        temperature=temperature or 0.5,
        api_key=api_key,
    )


if __name__ == "__main__":
    llm = init_model(fully_specified_name="gpt-4o-mini")
    print(llm.invoke("What is the capital of France?"))
