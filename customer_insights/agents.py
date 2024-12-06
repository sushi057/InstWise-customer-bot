from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_core.messages import ToolMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from customer_insights.state import AgentStateGraph
from customer_insights.tools import text_to_sql
from customer_insights.prompts import (
    # query_agent_prompt_template,
    data_agent_prompt_template,
    validation_agent_prompt_template,
    insights_agent_prompt_template,
)

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")
llm_mini = ChatOpenAI(model="gpt-4o-mini")


class ValidationResponse(BaseModel):
    response: bool = Field(..., description="The validation response from the agent.")


def data_agent(state: AgentStateGraph):
    """
    This agent executes the SQL query based on  the query agent.
    """

    # Validate SQL response with user query
    if isinstance(state["messages"][-1], ToolMessage):
        user_query = state["messages"][-3].content
        sql_response = state["messages"][-1].content

        validation_prompt = validation_agent_prompt_template.partial(
            user_query=user_query, query_response=sql_response
        )

        validation_chain = validation_prompt | llm_mini.with_structured_output(
            ValidationResponse
        )
        response = validation_chain.invoke({})

        # If sql query response doesn't match user query, prompt data agent to try again
        if not response.response:
            state["messages"].append(
                HumanMessage(
                    content="The SQL response does not match the user query. Please try again."
                )
            )

    data_agent_runnable = data_agent_prompt_template | llm.bind_tools(
        [text_to_sql], parallel_tool_calls=False
    )
    response = data_agent_runnable.invoke(state)
    return {**state, "messages": response}


def validation_agent(state: AgentStateGraph):
    """
    This agent validates the response from the data agent, wether it matches the user query or not.
    """
    query_response = state["messages"][-1].content
    user_query = state["messages"][-4].content

    model_with_structured_output = llm_mini.with_structured_output(ValidationResponse)

    validate_response_model = (
        validation_agent_prompt_template.partial(
            user_query=user_query, query_response=query_response
        )
        | model_with_structured_output
    )

    response = validate_response_model.invoke({})

    return {**state, "messages": AIMessage(content=str(response.response))}


def insights_agent(state: AgentStateGraph):
    """
    This agent provides insights based on the data.
    """
    insights_llm_with_tools = llm
    insights_agent_runnable = insights_agent_prompt_template | insights_llm_with_tools

    response = insights_agent_runnable.invoke(state)
    return {**state, "messages": response}
