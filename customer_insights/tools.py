import os
import boto3
from dotenv import load_dotenv
from typing import List, Optional, Dict
from pydantic import BaseModel

from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.messages import HumanMessage


load_dotenv()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    table_sources: Optional[str]
    result_set: Optional[List]
    metadata: Dict


def execute_sql_query(sql_query):
    """
    Runs a SQL query on the redshift database and returns the results.

    param sql_query: The SQL query to run.
    param_type sql_query: str
    """

    try:
        WORKGROUP_NAME = "tetsing"
        DATABASE_NAME = "dev"

        query_parts = sql_query.strip().split("::")
        sql_query = query_parts[-1]

        db_client = boto3.client(
            "redshift-data",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION_NAME"),
        )

        response = db_client.execute_statement(
            Database=DATABASE_NAME, WorkgroupName=WORKGROUP_NAME, Sql=sql_query
        )

        query_id = response["Id"]
        print(f"Query submitted. Query ID: {query_id}")

        while True:  # Busy wait until the query finishes
            status_response = db_client.describe_statement(Id=query_id)
            status = status_response["Status"]
            if status in ["FINISHED", "FAILED", "ABORTED"]:
                break
        # Check query status
        if status == "FINISHED":
            # Fetch the query results
            result_response = db_client.get_statement_result(Id=query_id)
            formatted_results = []
            for records in result_response["Records"]:
                row_dict = {}
                for column_metadata, fileds in zip(
                    result_response["ColumnMetadata"], records
                ):
                    row_dict[column_metadata["label"]] = (
                        None
                        if list(fileds.keys())[0] == "isNull"
                        else list(fileds.values())[0]
                    )
                formatted_results.append(row_dict)

            response = QueryResponse(
                table_sources=query_parts[0] if len(query_parts) > 1 else None,
                result_set=formatted_results,
                metadata={"status": status, "executed_query": sql_query},
            )

        else:
            response = QueryResponse(
                table_sources=query_parts[0] if len(query_parts) > 1 else None,
                result_set=None,
                metadata={"status": status, "executed_query": sql_query},
            )

        return response

    except Exception as e:
        return f"An error occurred: {e}"


nl2sql_prompt_template = """Given the following schema, convert the following natural language query to SQL
    Schema: 
    Database name: staging 
    
    companies table: [company_id, name, domain ]
    contacts table: [contact_id, first_name, last_name, email, company_name, created_at]
    deals table: [deal_id, dealname, amount, dealstage, pipeline, company_name, pipeline]
    tickets table: [ticket_id, subject, priority, status, company_name, created_at, assignee_id, requester_id, submitter_id, description, type, tags, satisfaction_rating, due_at, problem_id, raw_subject, has_incidents]
    meetings table: [meeting_id, created_at, archived_at, company_name, duration, subject, start_time, end_time]
    calls table: [call_id, created_at, archived_at, associated_companies, company_name]
    notes table: [note_id, created_at, archived_at, company_name, note_body]
    
    Guidelines:
    1. Perform table join carefully and use the appropriate column names and appropriate conditions.
    2. Dates and time are in ISO format.
    3. Do not add new lines inside the queries.
    4. Make sure you use correct column and table names as given in the schema.
    5. Do not perform data type casting on columns.
    6. The words "Company", "Organization", and "companies" are used interchangeably.
    7. If a query requires specific columns, make sure to include only these columns in the SELECT clause.
    8. If a query requires directly retrieving data from multiple tables, return separate queries, one for each table. Separate the queries with a semicolon. 
        precede each query with a comment that describes which table it is pulling from. If it was pullling from multiple tables precede the single query with "Multiple tables::".       
           
    Natural Language Query: 'Show me the first 2 companies'
    SQL Query: companies:: SELECT * FROM staging.companies LIMIT 2;     
    
    Natural Language Query: 'Show me the top companies that have highest number of deals'
    SQL Query: Multiple tables:: SELECT c.company_id, c.name, c.domain, COUNT(d.deal_id) AS num_deals FROM staging.companies AS c
    JOIN staging.deals AS d
    ON c.company_id = d.company_id
    GROUP BY c.company_id, c.name, c.domain
    ORDER BY num_deals DESC
    LIMIT 10;
    
    Natural Language Query: 'Show me list of contacts, deals and open support tickets for Hilton'
    SQL Query: contacts:: SELECT * FROM staging.contacts WHERE company_name = 'Hilton'; deals:: SELECT * FROM staging.deals WHERE company_name = 'Hilton'; tickets:: SELECT * FROM staging.tickets WHERE company_name = 'Hilton' AND status = 'open';
    
    Natural Language Query: {nl_query}
    SQL Query:"""

nl2sql_prompt = PromptTemplate.from_template(nl2sql_prompt_template)


llm = OpenAI()
nl2sql_chain = nl2sql_prompt | llm


@tool
def text_to_sql(nl_query):
    """
    Converts a natural language query to SQL and runs the SQL query on the redshift database.
    param nl_query: The natural language query to convert to SQL and run.
    param_type nl_query: str
    """
    sql_query = nl2sql_chain.invoke([HumanMessage(content=nl_query)])
    sql_query = sql_query.split(";")
    print("Using query: ", sql_query)

    responses = []
    for query in sql_query:
        query = query.strip()
        if len(query.lower()) > 0:
            responses.append(execute_sql_query(query))

    return responses
    # return ToolMessage(content=responses)


if __name__ == "__main__":
    print(text_to_sql.invoke("Show me the top clients"))
