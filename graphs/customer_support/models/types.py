from typing import Callable, TypedDict

from langchain_core.prompts import ChatPromptTemplate


class SupportWorkflowAgents(TypedDict):
    """Defines the structure of the SupportWorkflowAgents model."""

    fetch_user_info: Callable
    primary_assistant: Callable
    primary_assistant_tools: list
    solution_agent: Callable
    solution_agent_tools: list
    followup_agent: Callable
    followup_agent_tools: list


class SupportWorkflowPrompts(TypedDict):
    """Defines the structure of the SupportWorkflowPrompts model"""

    primary_assistant_prompt: ChatPromptTemplate
    solution_prompt: ChatPromptTemplate
    followup_prompt: ChatPromptTemplate
