from langchain_openai import ChatOpenAI

from customer_insights.state import AgentStateGraph
from customer_insights.tools import tools, query_agent_tools
from customer_insights.prompts import (
    query_agent_prompt_template,
    customer_data_agent_prompt_template,
    insights_agent_prompt_template,
)

llm = ChatOpenAI(model="gpt-4o")


def query_agent(state: AgentStateGraph):
    """
    This agent analyses user's query and parses information to fetch in messages
    """
    query_llm_with_tools = llm.bind_tools(query_agent_tools)
    query_agent_runnable = query_agent_prompt_template | query_llm_with_tools

    response = query_agent_runnable.invoke({"messages": state["messages"]})

    return {**state, "messages": response}


def customer_data_agent(state: AgentStateGraph):
    """
    This agent is responsible for fetching the customer data.
    """
    customer_data_agent_llm = llm.bind_tools(tools)
    customer_data_agent_runnable = (
        customer_data_agent_prompt_template | customer_data_agent_llm
    )
    response = customer_data_agent_runnable.invoke(state)

    return {**state, "messages": response}


def insights_agent(state: AgentStateGraph):
    """
    This agent provides insights based on the data.
    """
    insights_llm_with_tools = llm
    insights_agent_runnable = insights_agent_prompt_template | insights_llm_with_tools
    response = insights_agent_runnable.invoke(
        {
            "message": state["messages"],
        }
    )

    return {**state, "messages": response}
