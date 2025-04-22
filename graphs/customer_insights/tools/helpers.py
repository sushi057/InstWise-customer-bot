from graphs.customer_insights.tools.models import (
    CreateNLTOSQLPromptsArgs,
    NLTOSQLPrompts,
)


def create_nltosql_prompts(
    prompts: CreateNLTOSQLPromptsArgs,
) -> NLTOSQLPrompts:
    """Create prompts for NLTOSQL tool.

    Args:
        prompts: NLTOSQL prompts

    Returns:
        - schema prompt
        - nltosql prompt
        - abstract queries prompt
    """
    schema_data = prompts["schema_prompt"]
    nltosql_prompt = prompts["nltosql_prompt"]
    abstract_queries_prompt = prompts["abstract_queries_prompt"]
    database_name = prompts["database_name"]

    ######### schema for the database
    schema = f"""
Database Name: {database_name}

{schema_data}
"""

    ######### abstract_query_handler_template
    abstract_query_handler_template = (
        f"""
Given the schema: {schema} 

{abstract_queries_prompt}

"""
        + """

**If the user_query does not have it's respective final query, return original user query as the final query.**

User Query: {nl_query}
Updated Query:
Final Query:
"""
    )

    ######### nltosql_prompt_template
    nltosql_prompt_template = (
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

    return {
        "schema_prompt": schema,
        "nltosql_prompt": nltosql_prompt_template,
        "abstract_queries_prompt": abstract_query_handler_template,
    }
