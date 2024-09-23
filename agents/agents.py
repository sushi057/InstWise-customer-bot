from typing import Literal
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import END
from langgraph.prebuilt import tools_condition
from pydantic import BaseModel, Field

from models.openai_model import get_openai_model
from states.state import State
from tools.tools import (
    fetch_user_info,
    fetch_pending_issues,
    fetch_support_status,
    greet_user,
    lookup_activity,
    rag_call,
    recommendation_rag_call,
    suggest_workaround,
    log_activity,
    create_ticket,
    upsell_rag_call,
    personalized_follow_up,
)
from prompts.prompts import (
    greeting_prompt,
    primary_assistant_prompt,
    investigation_prompt,
    solution_prompt,
    recommendation_prompt,
    upsell_prompt,
    survey_prompt,
    log_prompt,
)


llm = get_openai_model()


class CompleteOrEscalate(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the main assistant,
    who can re-route the dialog based on the user's needs."""

    cancel: bool = True
    reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "cancel": True,
                "reason": "User changed their mind about the current task.",
            },
            "example 2": {
                "cancel": True,
                "reason": "I have fully completed the task.",
            },
            "example 3": {
                "cancel": False,
                "reason": "I need to search the user's emails or calendar for more information.",
            },
        }


greeting_tools = [fetch_user_info, fetch_pending_issues]
greeting_agent_runnable = greeting_prompt | llm.bind_tools(
    greeting_tools + [CompleteOrEscalate]
)


def route_greeting_agent(
    state: State,
) -> Literal["greeting_agent_tools", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    # tool_calls = state["messages"][-1].tool_calls
    # did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    # if did_cancel:
    #     return "leave_skill"

    return "greeting_agent_tools"


investigation_tools = [fetch_support_status, suggest_workaround]
investigation_runnable = investigation_prompt | llm.bind_tools(
    investigation_tools + [CompleteOrEscalate]
)


def route_investigation_agent(
    state: State,
) -> Literal["investigation_agent_tools", "leave_skill", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"

    return "investigation_agent_tools"


solution_tools = [rag_call, suggest_workaround]
solution_runnable = solution_prompt | llm.bind_tools(
    solution_tools + [CompleteOrEscalate]
)


def route_solution_agent(
    state: State,
) -> Literal["solution_agent_tools", "leave_skill", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"

    return "solution_agent_tools"


recommendation_tools = [recommendation_rag_call]
recommendation_runnable = recommendation_prompt | llm.bind_tools(
    recommendation_tools + [CompleteOrEscalate]
)


def route_recommendation_agent(
    state: State,
) -> Literal["recommendation_agent_tools", "leave_skill", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"

    return "recommendation_agent_tools"


upsell_tools = [upsell_rag_call, personalized_follow_up]
upsell_runnable = upsell_prompt | llm.bind_tools(upsell_tools + [CompleteOrEscalate])


def route_upsell_agent(
    state: State,
) -> Literal["upsell_agent_tools", "leave_skill", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"

    return "upsell_agent_tools"


log_tools = [log_activity, create_ticket]
log_runnable = log_prompt | llm.bind_tools(log_tools + [CompleteOrEscalate])


def route_log_agent(
    state: State,
) -> Literal["log_agent_tools", "leave_skill", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"

    return "log_agent_tools"


survey_tools = []
survey_runnable = survey_prompt | llm.bind_tools([CompleteOrEscalate])


def route_survey_agent(
    state: State,
) -> Literal["survey_agent_tools", "leave_skill", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    if did_cancel:
        return "leave_skill"

    return "survey_agent_tools"


# Primary Assistant
# Investigation, Solution, Recommendation, Log, Upsell, Survey


class ToInvestigationAgent(BaseModel):
    """Transfer work to the investigation agent to handle activity lookup and support status."""

    user_query: str = Field(description="The user's query to investigate.")


class ToSolutionAgent(BaseModel):
    """Transfer work to the solution agent to handle the RAG call and suggest a workaround."""

    user_query: str = Field(description="The user's query to find a solution for.")


class ToRecommendationAgent(BaseModel):
    """Transfer work to the recommendation agent to handle the recommendation RAG call and suggest a workaround."""

    user_query: str = Field(
        description="The user's query to find a recommendation for."
    )


class ToLogAgent(BaseModel):
    """Transfer work to the log agent to handle the activity logging and ticket creation."""

    session_info: dict = Field(
        description="The details of the interaction to be recorded."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_info": {
                    "id": "123",
                    "customer_id": "456",
                    "subject": "Issue with the product",
                    "description": "The user is facing an issue with the product.",
                    "status": "open",
                    "priority": "high",
                    "created_at": "2022-01-01T12:00:00",
                    "assigned_to": "",
                }
            }
        }


class ToUpsellAgent(BaseModel):
    """Transfer work to the upsell agent to handle the upsell RAG call and personalized follow-up."""

    user_query: str = Field(description="The user's query to find an upsell for.")


class ToSurveyAgent(BaseModel):
    """Transfer work to the survey agent to handle the user feedback collection."""

    user_query: str = Field(description="The user's feedback to collect.")


def route_primary_assistant(
    state: State,
) -> Literal[
    "primary_assistant_tools",
    "enter_investigation_agent",
    "enter_solution_agent",
    "enter_recommendation_agent",
    "enter_log_agent",
    "enter_upsell_agent",
    "enter_survey_agent",
    "__end__",
]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        if tool_calls[0]["name"] == ToInvestigationAgent.__name__:
            return "enter_investigation_agent"
        elif tool_calls[0]["name"] == ToSolutionAgent.__name__:
            return "enter_solution_agent"
        elif tool_calls[0]["name"] == ToRecommendationAgent.__name__:
            return "enter_recommendation_agent"
        elif tool_calls[0]["name"] == ToLogAgent.__name__:
            return "enter_log_agent"
        elif tool_calls[0]["name"] == ToUpsellAgent.__name__:
            return "enter_upsell_agent"
        elif tool_calls[0]["name"] == ToSurveyAgent.__name__:
            return "enter_survey_agent"
        return "primary_assistant_tools"
    return ValueError("Invalid Route")


primary_assistant_tools = [fetch_user_info, fetch_pending_issues]
assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    primary_assistant_tools
    + [
        ToInvestigationAgent,
        ToSolutionAgent,
        ToRecommendationAgent,
        ToLogAgent,
        ToUpsellAgent,
        ToSurveyAgent,
    ]
)
