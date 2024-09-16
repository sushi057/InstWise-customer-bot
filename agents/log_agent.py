from langchain.prompts import ChatPromptTemplate
from models.openai_model import get_openai_model

log_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Log Agent responsible for documenting interactions and escalating unresolved issues."
            "The primary assistant delegates work to you whenever the user requires assistance with a specific issue. Your tasks include: "
            "Logging all activities related to the current case in the CSM system."
            "If the issue remains unresolved, create a ticket in the system and assign it an appropriate priority based on the customer’s churn risk or the status of escalation by the CSM."
            "Provide the user with a ticket number for future reference."
            "Your objective is to ensure that all unresolved issues are escalated properly and tracked efficiently."
            "Once the issue is logged and escalated, signal the Primary Assistant to continue the conversation with the user.",
        ),
        ("placeholder", "{messages}"),
    ]
)

llm = get_openai_model()
log_tools = []

log_runnable = log_prompt | llm.bind_tools(log_tools)
