import os
from typing import Union, cast

import requests
from fastapi import APIRouter, HTTPException
from langchain_openai import ChatOpenAI

from graphs.customer_insights.tools.tools import create_nl2sql_tool
from models.outreach import (
    CustomerListWithNegativeSentiments,
    GenerateEmailReplyRequest,
    GenerateEmailReplyResponse,
    GenerateEmailsRequest,
    GenerateEmailsResponse,
    PersonalizedEmailsList,
)
from prompts.outreach import (
    customers_with_negative_sentiments_prompt,
    personalized_emails_prompt,
)
from utils.helpers import fetch_organization_details

router = APIRouter(tags=["outreach"])

RAG_API_URL = os.getenv("RAG_API_URL", "")
rag_api_headers = {"X-API-KEY": f"{os.getenv('X_API_KEY')}"}

llm = ChatOpenAI(model="gpt-4o")

# LLM with structured output for getting customers with negative sentiments
structured_llm_for_negative_sentiments = llm.with_structured_output(
    CustomerListWithNegativeSentiments
)
structured_llm_for_personalized_emails = llm.with_structured_output(
    PersonalizedEmailsList
)


@router.post("/generate-email-reply", response_model=GenerateEmailReplyResponse)
async def generate_email_reply(request: GenerateEmailReplyRequest):
    """
    Generate email body using the response from RAG with email body title, email subject and email body.
    """
    try:
        rag_query = f"Generate an email reply for for email body title as {request.email_body_title} with subject {request.subject} for {request.customer_name}."

        response = requests.get(
            RAG_API_URL,
            params={"query": rag_query, "company_id": request.org_id},
            headers=rag_api_headers,
        )

        return GenerateEmailReplyResponse(
            email_body=response.json()["results"]["answer"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/generate-outreach-emails",
    response_model=Union[list[GenerateEmailsResponse], list],
)
async def send_email(request: GenerateEmailsRequest):
    """
    Generate personalized outreach emails for the customers with overall negative sentiments.
    """
    try:
        prompts = fetch_organization_details(request.org_id)["org"]
        query_database = create_nl2sql_tool(
            schema_prompt=prompts["schema_prompt"],
            nltosql_prompt=prompts["nltosql_prompt"],
            abstract_queries_prompt=prompts["abstract_refinement_prompt"],
        )

        fetch_sentiment_query = "Fetch everything in tickets, tickets comments, conversation and feedbacks for 5 customers."
        sentiment_response = query_database(fetch_sentiment_query)

        customers_with_negative_sentiments_chain = (
            customers_with_negative_sentiments_prompt
            | structured_llm_for_negative_sentiments
        )
        customers_with_negative_sentiments = cast(
            CustomerListWithNegativeSentiments,
            customers_with_negative_sentiments_chain.invoke(
                {
                    "customer_sentiments": sentiment_response,
                }
            ),
        )

        personalized_emails_chain = (
            personalized_emails_prompt | structured_llm_for_personalized_emails
        )
        personalized_emails = cast(
            PersonalizedEmailsList,
            personalized_emails_chain.invoke(
                {
                    "customers_with_negative_sentiments": customers_with_negative_sentiments.customers
                }
            ),
        )

        if personalized_emails.emails:
            return [
                GenerateEmailsResponse(
                    email_from="sushilbhattachan@gmail.com",
                    email_to=email_item.email_to,
                    subject=email_item.subject,
                    email_body=email_item.email_body,
                )
                for email_item in personalized_emails.emails
            ]
        else:
            return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
