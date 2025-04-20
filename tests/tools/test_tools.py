from unittest.mock import MagicMock, patch

from graphs.customer_insights.tools import nltosql_tool
from utils.helpers import fetch_organization_details


@patch("graphs.customer_insights.tools.nltosql_tool.create_execute_sql_query_function")
@patch("graphs.customer_insights.tools.nltosql_tool.create_nltosql_prompts")
@patch("graphs.customer_insights.tools.nltosql_tool.ChatOpenAI")
@patch("graphs.customer_insights.tools.nltosql_tool.PromptTemplate")
def test_query_database_tool(
    mock_prompt_template,
    mock_chat_openai,
    mock_create_nltosql_prompts,
    mock_create_execute_sql_query_function,
):
    mock_create_nltosql_prompts.return_value = {
        "schema_prompt": "schema",
        "nltosql_prompt": "nltosql",
        "abstract_queries_prompt": "abstract",
    }
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = MagicMock(abstract_query="SELECT 1")
    mock_prompt_template.from_template.return_value = mock_chain
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_chain
    mock_chat_openai.return_value = mock_llm
    mock_create_execute_sql_query_function.return_value = lambda x: "executed"

    prompts = fetch_organization_details("66158fe71bfe10b58cb23eea")

    query_database, _ = nltosql_tool.create_nltosql_tool(
        database_name=prompts.database_name,
        schema_prompt=prompts.schema_prompt,
        nltosql_prompt=prompts.nltosql_prompt,
        abstract_queries_prompt=prompts.abstract_queries_prompt,
        redshift_db=prompts.redshift_db,
        redshift_work_space=prompts.redshift_work_space,
    )

    # Test that the returned query_database tool is callable and returns expected mock
    result = query_database.invoke("Show me list of 5 customers")

    assert isinstance(result, list)
    assert isinstance(result, list)
