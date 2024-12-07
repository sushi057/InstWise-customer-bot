import os
import boto3
from dotenv import load_dotenv

from langchain_core.tools import tool

# from langchain_core.runnables.config import RunnableConfig
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# from pprint import pprint
from langchain_core.messages import HumanMessage
from tools.prompts import abstract_query_handler_template, nl2sql_prompt_template
from tools.DTOs import QueryResponse


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


nl2sql_prompt = PromptTemplate.from_template(nl2sql_prompt_template)

abstract_query_handler = PromptTemplate.from_template(abstract_query_handler_template)

llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=512)
# nl2sql_chain = abstract_query_handler | llm | nl2sql_prompt | llm

abstract_query_chain = abstract_query_handler | llm
nl2sql_chain = nl2sql_prompt | llm


@tool
def query_database(nl_query):
    """
    Converts a natural language query to SQL and runs the SQL query on the redshift database.
    param nl_query: The natural language query to convert to SQL and run.
    param_type nl_query: str
    """
    abstract_query_response = abstract_query_chain.invoke(
        HumanMessage(content=nl_query)
    )
    sql_query = nl2sql_chain.invoke(
        [HumanMessage(content=abstract_query_response.content)]
    )
    # sql_query = nl2sql_chain.invoke([HumanMessage(content=nl_query)])
    sql_query = sql_query.content.split(";")
    print("Using query: ", sql_query)

    responses = []
    for query in sql_query:
        query = query.strip()
        if len(query.lower()) > 0:
            responses.append(execute_sql_query(query))
    return responses
