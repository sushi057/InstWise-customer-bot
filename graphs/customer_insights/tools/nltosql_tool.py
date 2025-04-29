import logging
import os
from typing import Optional, cast

import boto3
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.config import get_stream_writer
from langsmith import traceable

from graphs.customer_insights.tools.helpers import create_nltosql_prompts
from graphs.customer_insights.tools.models import AbstractQueryResponse, QueryResponse

load_dotenv()

logger = logging.getLogger(__name__)


def create_execute_sql_query_function(workgroup_name: str, redshift_db: str):
    """Create execute_sql_query function to run SQL queries on given redshift database.

    Args:
        workgroup_name: Redshift workgroup name
        database_name: Redshift database name

    Returns:
        execute_sql_query
    """

    @traceable(run_type="tool", name="execute_sql_query")
    def execute_sql_query(sql_query):
        """
        Runs a SQL query on the redshift database and returns the results.
        param sql_query: The SQL query to run.
        param_type sql_query: str
        """

        try:
            WORKGROUP_NAME = workgroup_name
            REDSHIFT_DB = redshift_db

            query_parts = sql_query.strip().split("::")
            sql_query = query_parts[-1]

            db_client = boto3.client(
                "redshift-data",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_REGION_NAME"),
            )

            logger.info(f"Executing SQL query: {sql_query}")
            response = db_client.execute_statement(
                Database=REDSHIFT_DB, WorkgroupName=WORKGROUP_NAME, Sql=sql_query
            )

            query_id = response["Id"]

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
                    for column_metadata, fields in zip(
                        result_response["ColumnMetadata"], records
                    ):
                        row_dict[column_metadata["label"]] = (
                            None
                            if list(fields.keys())[0] == "isNull"
                            else list(fields.values())[0]
                        )
                    formatted_results.append(row_dict)

                response = QueryResponse(
                    table_sources=query_parts[0] if len(query_parts) > 1 else None,
                    result_set=formatted_results,
                    metadata={"status": status, "executed_query": sql_query},
                )

                logger.info(
                    f"Redshift query finished successfully. Query ID: {query_id}"
                )
            else:
                response = QueryResponse(
                    table_sources=query_parts[0] if len(query_parts) > 1 else None,
                    result_set=None,
                    metadata={"status": status, "executed_query": sql_query},
                )
                logger.warning(
                    f"Redshift query failed. Query ID: {query_id}, Status: {status}"
                )

            return response

        except Exception as e:
            logger.exception(f"Error executing SQL query: {sql_query}, Error: {e}")
            raise Exception(f"Error executing query: {e}")

    return execute_sql_query


def create_nltosql_tool(
    *,
    database_name: str,
    redshift_work_space: str,
    redshift_db: str,
    schema_prompt: str,
    nltosql_prompt: str,
    abstract_queries_prompt: str,
    chat_model: Optional[BaseChatModel] = None,
):
    """Create extract_database (nltosql) tool with latest prompts.

    Args:
        schema_prompt: str
        nltosql_prompt: str
        abstract_queries_prompt: str
        database_name: str
        redshift_work_space: str
        redshift_db: str

    Returns:
        - query_database tool
        - abstract query chain
    """

    try:
        if not database_name or not redshift_work_space or not redshift_db:
            raise Exception(
                "Database name, redshift work space and redshift db are required."
            )

        execute_sql_query = create_execute_sql_query_function(
            redshift_work_space, redshift_db
        )

        final_prompts = create_nltosql_prompts(
            {
                "schema_prompt": schema_prompt,
                "nltosql_prompt": nltosql_prompt,
                "abstract_queries_prompt": abstract_queries_prompt,
                "database_name": database_name,
            }
        )

        abstract_query_handler = PromptTemplate.from_template(
            final_prompts["abstract_queries_prompt"]
        )
        nltosql_prompt_handler = PromptTemplate.from_template(
            final_prompts["nltosql_prompt"]
        )

        if not chat_model:
            llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_completion_tokens=512)
        else:
            llm = chat_model

        # Create chains for abstract query and nltosql
        abstract_query_chain = abstract_query_handler | llm.with_structured_output(
            AbstractQueryResponse
        )
        nltosql_chain = nltosql_prompt_handler | llm

        @tool
        def query_database(nl_query: str):
            """
            Converts a natural language query to SQL and runs the SQL query on the redshift database.
            param nl_query: The natural language query to convert to SQL and run.
            param_type nl_query: str
            """

            writer = get_stream_writer()
            abstract_query_response = cast(
                AbstractQueryResponse,
                abstract_query_chain.invoke({"nl_query": nl_query}),
            )
            sql_query = nltosql_chain.invoke(
                {"nl_query": abstract_query_response.abstract_query}
            )
            sql_query = sql_query.content.split(";")  # type: ignore

            # Clean up SQL query formatting if wrapped in code block
            sql_query = [
                q.replace("```sql", "").replace("```", "").strip()
                for q in sql_query
                if q.strip()
            ]

            responses = []
            for query in sql_query:
                if len(query.lower()) > 0:
                    information_source = query.split("::")[0]
                    writer(
                        {
                            "status": f"Fetching information {information_source}",
                        }
                    )
                    res = execute_sql_query(query)
                    responses.append(res)

            return responses

        return query_database, abstract_query_chain

    except Exception as e:
        logger.exception(f"Error creating NLTOSQL tool: {e}")
        raise Exception(f"Error creating NLTOSQL tool: {e}")
