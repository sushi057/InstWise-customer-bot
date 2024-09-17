from typing import Literal
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import END
from langgraph.prebuilt import tools_condition

from models.openai_model import get_openai_model
from states.state import State
from tools.tools import (
    fetch_user_info,
    fetch_pending_issues,
    fetch_support_status,
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

primary_assistant_tools = []
assistant_runnable = primary_assistant_prompt | llm


def route_primary_assistant(
    state: State,
) -> Literal[
    "investigation_agent",
    "solution_agent",
    "recommendation_agent",
    "log_agent",
    "upsell_agent",
    "survey_agent",
    "__end__",
]:
    route = tools_condition(state)
    if route == END:
        return END


greeting_tools = [fetch_user_info, fetch_pending_issues]
greeting_agent_runnable = greeting_prompt | llm.bind_tools(greeting_tools)


def route_greeting_agent(
    state: State,
) -> Literal["greeting_agent_tools", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    tool_names = [t.name for t in tool_calls]
    if all(tc["name"] in tool_names for tc in tool_calls):
        return "greeting_agent_tools"


def route_investigation_agent(
    state: State,
) -> Literal["investigation_agent_tools", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    tool_names = [t.name for t in tool_calls]
    if all(tc["name"] in tool_names for tc in tool_calls):
        return "investigation_agent_tools"


def route_solution_agent(
    state: State,
) -> Literal["solution_agent_tools", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    tool_names = [t.name for t in tool_calls]
    if all(tc["name"] in tool_names for tc in tool_calls):
        return "solution_agent_tools"


def route_recommendation_agent(
    state: State,
) -> Literal["recommendation_agent_tools", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    tool_names = [t.name for t in tool_calls]
    if all(tc["name"] in tool_names for tc in tool_calls):
        return "recommendation_agent_tools"


def route_log_agent(
    state: State,
) -> Literal["log_agent_tools", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    tool_names = [t.name for t in tool_calls]
    if all(tc["name"] in tool_names for tc in tool_calls):
        return "log_agent_tools"


def route_upsell_agent(
    state: State,
) -> Literal["upsell_agent_tools", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    tool_names = [t.name for t in tool_calls]
    if all(tc["name"] in tool_names for tc in tool_calls):
        return "upsell_agent_tools"


def route_survey_agent(
    state: State,
) -> Literal["survey_agent_tools", "__end__"]:
    route = tools_condition(state)
    if route == END:
        return END

    tool_calls = state["messages"][-1].tool_calls
    tool_names = [t.name for t in tool_calls]
    if all(tc["name"] in tool_names for tc in tool_calls):
        return "survey_agent_tools"


investigation_tools = [lookup_activity, fetch_support_status]
investigation_runnable = investigation_prompt | llm.bind_tools(investigation_tools)

solution_tools = [rag_call, suggest_workaround]
solution_runnable = solution_prompt | llm.bind_tools(solution_tools)

recommendation_tools = [recommendation_rag_call, suggest_workaround]
recommendation_runnable = recommendation_prompt | llm.bind_tools(recommendation_tools)

upsell_tools = [upsell_rag_call, personalized_follow_up]
upsell_runnable = upsell_prompt | llm.bind_tools(upsell_tools)

log_tools = [log_activity, create_ticket]
log_runnable = log_prompt | llm.bind_tools(log_tools)

survey_tools = []
survey_runnable = survey_prompt | llm
