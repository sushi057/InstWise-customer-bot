from graphs.customer_insights.tools.nltosql_tool import (
    create_execute_sql_query_function,
    create_nltosql_tool,
)
from utils.helpers import fetch_organization_details

while True:
    user_query = input(
        "Press 'd' for query_database tool, press 's' to run sql query or press 'q' to quit: "
    )
    if user_query in ["q", "quit"]:
        break

    org_details = fetch_organization_details("66158fe71bfe10b58cb23eea")
    if user_query == "d":
        user_query = input("Enter natural language query: ")
        query_database, _ = create_nltosql_tool(
            database_name=org_details.database_name,
            schema_prompt=org_details.schema_prompt,
            nltosql_prompt=org_details.nltosql_prompt,
            abstract_queries_prompt=org_details.abstract_queries_prompt,
            redshift_db=org_details.redshift_db,
            redshift_work_space=org_details.redshift_work_space,
        )

        print(query_database.invoke(user_query))

    else:
        user_query = input("Enter SQL query: ")
        execute_sql_query = create_execute_sql_query_function(
            workgroup_name=org_details.redshift_work_space,
            redshift_db=org_details.redshift_db,
        )

        print(execute_sql_query(user_query))
