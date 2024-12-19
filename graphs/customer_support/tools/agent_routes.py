from pydantic import BaseModel, Field


class ToSolutionAgent(BaseModel):
    """Transfer work to the solution agent to handle the RAG call and suggest a workaround."""

    user_query: str = Field(description="The user's query to find a solution for.")


class ToLogAgent(BaseModel):
    """Transfer work to the log agent to handle the activity logging and ticket creation."""

    session_info: dict = Field(
        ..., description="The details of the interaction to be recorded."
    )


class ToFollowUpAgent(BaseModel):
    """Transfer work to the follow-up agent to handle the personalized follow-up."""

    # status: str = Field(..., description="The status of the user's issue.")
