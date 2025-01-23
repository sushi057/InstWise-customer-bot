from langchain_core.prompts import ChatPromptTemplate

customers_with_negative_sentiments_prompt = ChatPromptTemplate(
    [
        (
            "system",
            """
The following information contains tickets, tickets comments, conversation and feedbacks with rating for different customers.

<Customer Sentiments>
{customer_sentiments}
</Customer Sentiments>

Review the above information and summarize sentiments concisely for each customer with score from 1 to 5, where 1 is negative and 5 is positive.

**Do not fabricate any information. Use the provided data to generate your output.**

""",
        )
    ]
)

personalized_emails_prompt = ChatPromptTemplate(
    [
        (
            "system",
            """
The following information contains customers with overall negative sentiments.

<Customers with Negative Sentiments>
{customers_with_negative_sentiments}
</Customers with Negative Sentiments>

Review the above information and generate personalized, empathetic emails for each customer with negative sentiments. Ensure the emails acknowledge their concerns, offer sincere apologies, and being taken to address their issues. 
This mail is supposed to be an outreach mail without any specific concern or issues. Aim to preserve the customer relationship and rebuild trust.
The best regards should be from Sushil Bhattachan, Customer Success Team.

""",
        )
    ]
)
