from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from pydantic import BaseModel, Field


class CustomerIDs(BaseModel):
    """
    This class defines the structure of the customer information that will be used in the agent state graph.
    """

    customer_id: str = Field(..., description="The customer's unique identifier.")
    name: str = Field(..., description="The customer's name.")
    email: str = Field(..., description="The customer's email address.")
    crm_customer_id: int = Field(..., description="The customer's CRM ID.")
    csm_customer_id: int = Field(..., description="The customer's CSM ID.")
    accounting_customer_id: int = Field(
        ..., description="The customer's accounting ID."
    )
    helpdesk_customer_id: int = Field(..., description="The customer's helpdesk ID.")


class AgentStateGraph(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    CustomerIDs: CustomerIDs
    crm_agent_response: str
    csm_agent_response: str
    helpdesk_agent_response: str
    chatdata_agent_response: str
