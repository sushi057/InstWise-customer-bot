import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def insert_into_redshift(data_dict):
    """
    Accepts Dictionary of data to be inserted into customer_engagement_summary
    """
    try:
        # Initialize Redshift Data API client
        db_client = boto3.client(
            "redshift-data",
            aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key= os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name= os.getenv("AWS_REGION_NAME"),
        )
        
        # Define SQL insert query
        insert_query = f"""
            INSERT INTO {os.getenv("REDSHIFT_DB")}.{os.getenv("DATABASE_NAME")}.Customer_Engagement_Summary 
            (tenant_id, week_date, sentiment, opportunity, risk, followup) 
            VALUES ('{data_dict["tenant_id"]}', '{data_dict["week_date"]}', '{data_dict["sentiment"]}', 
                    '{data_dict["opportunity"]}', '{data_dict["risk"]}', '{data_dict["followup"]}')
        """

        print("Data insertion initiated for the CES data")
        # Execute the query
        response = db_client.execute_statement(
            Database=os.getenv("REDSHIFT_DB"),
            WorkgroupName=os.getenv("REDSHIFT_WORK_GROUP"),
            Sql=insert_query
        )
        
        print("Response:", response)
    except Exception as e:
        print(f"Error inserting data: {e}")