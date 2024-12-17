import os
from dotenv import load_dotenv

load_dotenv()

schema = f"""Database name: {os.getenv("DATABASE_NAME")}
companies table: [company_id,  name,  domain,  is_active,  start_date,  end_date ]
contacts table: [contact_id,  first_name,  last_name,  email,  company_name,  created_date]
deals table: [deal_id,  dealname,  amount,  dealstage,  company_name,  created_at,  closedate]
tickets table: [ticket_id,  subject,  priority,  status,  company_name,  created_at,  assignee_id,  requester_id,  submitter_id,  description,  ticket_type,  tags,  satisfaction_rating,  due_at,  updated_at, comment, comment_date]
meetings table: [meeting_id,  created_at,  updated_at,  company_name,  duration,  subject]
calls table: [call_id,  created_at,  updated_at,  company_name]
notes table: [note_id,  created_at,  company_name,  note_body]
meetings table: [meeting_id,  created_at,  updated_at,  company_name,  duration,  subject]
calls table: [call_id,  created_at,  updated_at,  company_name]
notes table: [note_id,  created_at,  company_name,  note_body]
customer_features table: [feature_id, created_at, updated_at, feature_description, feature_date, email, company_name, version, start_date, end_date]
customer_logins table: [login_id, created_at, updated_at, login_date, email, company_name, version, start_date, end_date]
customer_conversations table: [conversation_id, created_at, updated_at, conversation_session, question, answer, session_order, user_id, start_date, end_date]
feedback table: [feedback_id, created_at, updated_at, user_email, feedback_description, reported_query, rating, start_date, end_date]
customer_health: [company_id, customer_name, opened_deals, closed_deals, lost_deals, no_conversations, unique_features, overall_features, number_of_logins, last_login, total_ticket_count, open_ticket_count, escalated_ticket_count, closed_ticket_count]    
"""

nl2sql_prompt_template = (
    f"""Given the following schema, convert the following natural language query to SQL
Schema: 
Shcema: 
{schema}

Guidelines:
1. Perform table join carefully and use the appropriate column names and appropriate conditions.
2. Dates and time are in ISO format.
3. Do not add new lines inside the queries.
4. Make sure you use correct column and table names as given in the schema.
5. Do not perform data type casting on columns.
6. The words "Company", "Organization", "customer", and "companies" are used interchangeably.
7. If a query requires specific columns, make sure to include only these columns in the SELECT clause.
8. If a query requires directly retrieving data from multiple tables, return separate queries, one for each table. Separate the queries with a semicolon. 
    precede each query with a comment that describes which table it is pulling from. If it was pullling from multiple tables precede the single query with "Multiple tables::".       
        
Natural Language Query: Show me the first 2 companies separately
SQL Query: companies:: SELECT * FROM {os.getenv("DATABASE_NAME")}.companies LIMIT 2;     

Natural Language Query: Show me the top companies that have highest number of deals separately
SQL Query: Multiple tables:: SELECT c.company_id, c.name, c.domain, COUNT(d.deal_id) AS num_deals FROM {os.getenv("DATABASE_NAME")}.companies AS c
JOIN {os.getenv("DATABASE_NAME")}.deals AS d
ON c.name = d.company_name
GROUP BY c.company_id, c.name, c.domain
ORDER BY num_deals DESC
LIMIT 10;

Natural Language Query: Show me list of contacts, deals and open support tickets for Hyatt separately 
SQL Query: contacts:: SELECT * FROM {os.getenv("DATABASE_NAME")}.contacts WHERE company_name = 'Hyatt'; deals:: SELECT * FROM {os.getenv("DATABASE_NAME")}.deals WHERE company_name = 'Hyatt'; tickets:: SELECT * FROM {os.getenv("DATABASE_NAME")}.tickets WHERE company_name = 'Hyatt' AND status = 'open';

Natural Language Query: Show me the health of the Hyatt
SQL Query: customer_health:: SELECT * FROM reporting.customer_health WHERE customer_name = 'Hyatt'

Natural Language Query: Show me the list of contacts for Hyatt
SQL Query: contacts:: SELECT contacts.first_name, contacts.last_name, contacts.email FROM {os.getenv("DATABASE_NAME")}.contacts WHERE company_name = 'Hyatt';

Natural Language Query: Fetch customer name where domain is hyatt.com
SQL Query: companies:: SELECT * FROM reporting.companies WHERE domain = 'hyatt.com';

Natural Language Query: Show login trend for Hilton by month.
SQL Query: "customer_logins:: SELECT DATE_TRUNC('month', login_date) AS month, COUNT(login_id) AS login_count FROM reporting.customer_logins WHERE company_name = 'Hilton' GROUP BY month ORDER BY month
"""
    + """Natural Language Query: {nl_query} separately
SQL Query:"""
)

abstract_query_handler_template = (
    f"""
Given the schema: {schema} """
    + """
Please check if the query is abstract meaning it does not define what field and condition to look for. And if it’s abstract form the natural language like query, if not just show the same as it’s coming from the user. Do not worry about exact field but should actually quantify the rule. Do not explain the reason etc. Just write updated query and not even user query. I just need to know the result. 

Here are some examples of User query and updated query. 
User Query: Show me summary of current state of Customer Hyatt 
Updated Query: Fetch all the information that you know about Hyatt

User Query: Show me customer sentiments for Hyatt
Updated Query:Get all the information related to Hyatt that has sentiments data, like Chat conversation, support survey, support ticket and activities, phone calls, meeting , notes, 

User Query: Which customer is most risky
Updated Query:Get list of top 5 customers that has highest total amount of deals pending , has low health score, highest number of open tickets, low average customer survey score

User Query: Write status report for Hyatt that I need to send it my boss
Updated Query:Get all the information that you know about Hyatt, even including activities of Support Tickets

User Query: I need to meet with Jim from Hyatt , please let me know if I should be caution about anything
Updated Query:Get all the information that has customer sentiments data, like Chat conversation, support survey, support ticket and activities, phone calls, meeting , notes, 

User Query: Which customer should I prioritize
Updated Query:Get list of top 5 customers that has highest total amount of deals pending , has low health score, highest number of open tickets, low average customer survey score and that are close to renewal date

User Query: Which of our top revenue-generating customers are at high or medium risk?
Updated Query:Get list of top 5 customers that has highest ARR , has low health score, highest number of open tickets, low average customer survey score and that are close to renewal date

User Query: Show me all customer information for Hyatt
Updated Query: Show me all customer information for Hyatt

User Query: Show me all the contacts and support ticket for Hyatt
Updated query: Show me all the contacts and support ticket for Hyatt

User Query: Show to top 5 customers with highest amount of deals and highest open tickets
Updated  Query: Show to top 5 customers with highest amount of deals and highest open tickets

User Query: Fetch customer name for domain hyatt.com
Updated Query: Fetch customer name where domain is hyatt.com

User Query: I am meeting with Support Manager today. Analyze the the support tickets and comments and see user of company has negative sentiments, so that I can talk to him. Show me top 3 companies with negative sentiments.
Updated Query: Fetch all support tickets and ticket comments related to all the customers. 


User Query: {nl_query}
Updated Query:"""
)
