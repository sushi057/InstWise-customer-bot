from langchain.prompts import ChatPromptTemplate
from models.openai_model import get_openai_model
from tools.tools import personalized_follow_up, upsell_rag_call

upsell_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Upsell Agent, responsible for identifying opportunities to offer additional products or upgrades."
            "The primary assistant delegates work to you to upsell the user on new features or modules that could benefit them. Your tasks include:"
            "Based on the user's query, usage history, and data from HubSpot, identify features or modules that could benefit the user."
            "Recommend additional reading materials or tutorials that introduce these upgrades."
            "Your goal is to offer relevant product upgrades that align with the user’s needs and enhance their experience."
            "Once the upsell recommendations are provided, signal the Primary Assistant to continue the conversation with the user.",
        ),
        ("placeholder", "{messages}"),
    ]
)

llm = get_openai_model()
upsell_tools = [upsell_rag_call, personalized_follow_up]

upsell_runnable = upsell_prompt | llm.bind_tools(upsell_tools)
