import os

import boto3
from dotenv import load_dotenv
from langchain_core.tools import tool

from graphs.customer_insights.tools.models import AddCustomerEngagementSummaryArgs

load_dotenv()


@tool
def add_summary_to_redshift(data: AddCustomerEngagementSummaryArgs):
    """
    Insert customer engagement summary data into Redshift.
    """
    try:
        # Initialize Redshift Data API client
        db_client = boto3.client(
            "redshift-data",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION_NAME"),
        )

        # Define SQL insert query
        insert_query = f"""
            INSERT INTO {os.getenv("DATABASE_NAME")}.REPORTING.Customer_Engagement_Summary 
            (tenant_id, week_date, sentiment, opportunity, risk, followup) 
            VALUES ('{data.tenant_id}', '{data.week_date}', '{data.sentiment}', 
                    '{data.opportunity}', '{data.risk}', '{data.followup}')
        """

        # Execute the query
        response = db_client.execute_statement(
            Database="ss_dev",  # os.getenv("DATABASE_NAME"),
            WorkgroupName="tetsing",  # os.getenv("WORKGROUP_NAME"),
            Sql=insert_query,
        )

        print("Data insertion initiated.")
        print("Response:", response)
    except Exception as e:
        print(f"Error inserting data: {e}")
