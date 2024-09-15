from langchain.prompts import ChatPromptTemplate

from models.openai_model import get_openai_model
from tools.tools import fetch_customer_info, lookup_activity

greetings_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Greetings Agent responsible for welcoming customers to the support system. Your tasks include:"
            "Fetching the user information from Hubspot and greeting the user by their name or company name"
            "Checking Zendesk to see if the user has any unresolved or pending issues."
            "Listening to user's queries or inquiries and responding to them in a friendly and professional manner."
            "If pending issues are found, ask the user if they are inquiring about those issues."
            "Your objective is to make the user feel welcome and streamline the support process by addressing any ongoing cases early."
            "Once the initial greeting is complete, signal the Primary Assistant continue the conversation with the user.",
        ),
    ]
)

llm = get_openai_model()

greetings_tools = [fetch_customer_info, lookup_activity]
greeting_agent_runnable = greetings_prompt | llm.bind_tools(greetings_tools)
