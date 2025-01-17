import os
import boto3
from dotenv import load_dotenv

from langchain_core.tools import tool

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from graphs.customer_insights.tools.DTOs import QueryResponse
from utils.utils import fetch_organization_details
# from graphs.customer_insights.tools.prompts import (
#     abstract_query_handler_template,
#     nl2sql_prompt_template,
# )


load_dotenv()


def execute_sql_query(sql_query):
    """
    Runs a SQL query on the redshift database and returns the results.
    param sql_query: The SQL query to run.
    param_type sql_query: str
    """

    try:
        WORKGROUP_NAME = os.getenv("REDSHIFT_WORK_GROUP")
        DATABASE_NAME = os.getenv("REDSHIFT_DB")

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


def create_nl2sql_tool(
    schema_prompt: str, nltosql_prompt: str, abstract_queries_prompt: str
):
    """Create extract_database (nl2sql) tool with latest prompts."""

    # schema for the database
    schema = (
        f"""
Database Name: {os.getenv("DATABASE_NAME")}
"""
    ) + schema_prompt

    # nl2sql_prompt_template
    nl2sql_prompt_template = (
        f"""
Given the following schema, convert the following natural language query to SQL
Schema:
{schema}

{nltosql_prompt}
"""
        + """
Natural Language Query: {nl_query} separately
SQL Query:
"""
    )

    # abstract_query_handler_template
    abstract_query_handler_template = (
        f"""
Given the schema: {schema} 

{abstract_queries_prompt}

"""
        + """
User Query: {nl_query}
Updated Query
"""
    )

    # Update prompt template to pass database name
    nl2sql_prompt = PromptTemplate.from_template(nl2sql_prompt_template)
    abstract_query_handler = PromptTemplate.from_template(
        abstract_query_handler_template
    )

    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=512)
    abstract_query_chain = abstract_query_handler | llm
    nl2sql_chain = nl2sql_prompt | llm

    @tool
    def query_database(nl_query: str):
        """
        Converts a natural language query to SQL and runs the SQL query on the redshift database.
        param nl_query: The natural language query to convert to SQL and run.
        param_type nl_query: str
        """

        abstract_query_response = abstract_query_chain.invoke(nl_query)
        sql_query = nl2sql_chain.invoke(abstract_query_response.content)
        # sql_query = nl2sql_chain.invoke([HumanMessage(content=nl_query)])
        sql_query = sql_query.content.split(";")
        print("Using query: ", sql_query)

        responses = []
        for query in sql_query:
            query = query.strip()
            if len(query.lower()) > 0:
                responses.append(execute_sql_query(query))
        return responses

    return query_database


if __name__ == "__main__":
    user_query = input("Enter your query: ")
    prompts = fetch_organization_details("66158fe71bfe10b58cb23eea")["org"]

    query_database = create_nl2sql_tool(
        schema_prompt=prompts["schema_prompt"],
        nltosql_prompt=prompts["nltosql_prompt"],
        abstract_queries_prompt=prompts["abstract_refinement_prompt"],
    )
    print(query_database.invoke(user_query))
