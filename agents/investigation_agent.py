from langchain.prompts import ChatPromptTemplate
from models.openai_model import get_openai_model
from tools import lookup_activity

investigation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Investigation Agent responsible for gathering and assessing case history and investigating the issue."
            "The primary assistant delegates work to you whenever the user requires assistance with a specific issue. Your tasks include:"
            "Check activity from  Zendesk, Planhat, and HubSpot for case history related to the current issue."
            "Verifying if this is a known issue."
            "Determining if the issue has been escalated by a Customer Success Manager (CSM) in Planhat."
            "If any of the above checks return positive, craft a response to inform the user of the status and actions taken so far."
            "Once the investigation is complete, signal the Primary Assistant to continue the conversation with the user.",
        ),
        ("placeholder", "{messages}"),
    ]
)

llm = get_openai_model()

investigation_tools = [lookup_activity]
investigation_runnable = investigation_prompt | llm.bind_tools(investigation_tools)
