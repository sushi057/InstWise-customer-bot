from typing import Annotated, Optional

from pydantic import BaseModel, Field, EmailStr


class FeedbackModel(BaseModel):
    customer_id: str = Field(
        ..., alias="_id.$oid", description="The id of the customer giving feedback."
    )
    feedback: str = Field(..., description="The feedback given by the user.")
    rating: int = Field(..., description="The rating given by the user.")
