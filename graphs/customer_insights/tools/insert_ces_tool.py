import os
import time

import boto3
from dotenv import load_dotenv
from langchain_core.tools import tool

from .models import AddCustomerEngagementSummaryArgs

load_dotenv()


@tool
def insert_into_redshift(data: AddCustomerEngagementSummaryArgs):
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
            INSERT INTO {os.getenv("REDSHIFT_DB")}.{os.getenv("DATABASE_NAME")}.Customer_Engagement_Summary 
            (tenant_id, customer_id, week_date, sentiment, opportunity, risk, followup) 
            VALUES ('{data.tenant_id}', '{data.customer_id}', '{data.week_date}', '{data.sentiment}', 
                    '{data.opportunity}', '{data.risk}', '{data.followup}')
        """
        # Execute the query
        response = db_client.execute_statement(
            Database=os.getenv("REDSHIFT_DB"),
            WorkgroupName=os.getenv("REDSHIFT_WORK_GROUP"),
            Sql=insert_query,
        )

        statement_id = response["Id"]

        # Wait for execution to complete
        while True:
            desc = db_client.describe_statement(Id=statement_id)
            status = desc["Status"]
            print(f"Query Status: {status}")

            if status in ["FAILED", "FINISHED"]:
                break

            time.sleep(2)  # Wait before checking again
            return desc

        if status == "FAILED":
            print("Error:", desc["Error"])

    except Exception as e:
        print(f"Error inserting data: {e}")
