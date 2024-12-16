# from typing import Literal
# from langgraph.graph import END
# from langgraph.prebuilt import tools_condition
from pydantic import BaseModel

from models.openai_model import get_openai_model
from graphs.customer_support.states.state import State
from graphs.customer_support.tools.tools import (
    # fetch_user_info,
    # fetch_pending_issues,
    solution_rag_call,
    recommend_features,
    upsell_features,
    collect_feedback,
)
from graphs.customer_support.tools.agent_routes import (
    ToSolutionAgent,
    ToLogAgent,
    ToFollowUpAgent,
)
from graphs.customer_support.prompts.prompts import create_prompts

from graphs.customer_insights.tools.tools import query_database


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


primary_assistant_tools = [query_database]
solution_tools = [solution_rag_call]
followup_tools = [recommend_features, upsell_features, query_database]
log_tools = [collect_feedback]


def create_agents(org_id: str):
    prompts = create_prompts(org_id)

    llm = get_openai_model(model="gpt-4o")
    # llm_mini = get_openai_model(model="gpt-4o-mini")

    assistant_runnable = prompts["primary_assistant_prompt"] | llm.bind_tools(
        primary_assistant_tools + [ToSolutionAgent, ToLogAgent, ToFollowUpAgent]
    )

    solution_runnable = prompts["solution_prompt"] | llm.bind_tools(
        solution_tools + [CompleteOrEscalate]
    )

    followup_runnable = prompts["followup_prompt"] | llm.bind_tools(
        followup_tools + [CompleteOrEscalate]
    )

    log_runnable = prompts["log_prompt"] | llm.bind_tools(
        log_tools + [CompleteOrEscalate]
    )
    return {
        "assistant_runnable": assistant_runnable,
        "solution_runnable": solution_runnable,
        "followup_runnable": followup_runnable,
        "log_runnable": log_runnable,
    }
