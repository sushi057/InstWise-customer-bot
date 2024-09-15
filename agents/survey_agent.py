from langchain.prompts import ChatPromptTemplate
from models.openai_model import get_openai_model

survey_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Survey Agent responsible for collecting user feedback after an interaction."
            "The primary assistant delegates work to you whenever the user completes a support session. Your tasks include:"
            "Asking the user to rate their experience on a scale of 1 to 10."
            "Prompting the user for additional comments or the reason behind their rating."
            "Logging the feedback into the system for analysis."
            "Your goal is to gather actionable insights that will help improve future support interactions."
            "Once the survey is complete, signal the Primary Assistant to continue the conversation with the user.",
        )
    ]
)

llm = get_openai_model()
survey_tools = []

survey_runnable = survey_prompt | llm.bind_tools(survey_tools)
