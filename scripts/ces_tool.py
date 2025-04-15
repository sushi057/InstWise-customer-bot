from graphs.customer_insights.tools.insert_ces_tool import \
    insert_summary_in_redshift
from graphs.customer_insights.tools.models import \
    AddCustomerEngagementSummaryArgs

data = AddCustomerEngagementSummaryArgs(
    tenant_id="66158fe71bfe10b58cb23eea",
    customer_id="123",
    week_date="2025-03-25 22:07",
    sentiment="sentiment",
    opportunity="opportunity",
    risk="risk",
    followup="followup",
)

if __name__ == "__main__":
    print(
        insert_summary_in_redshift.invoke(
            {
                "data": {
                    "tenant_id": "Hilton",
                    "customer_id": "Hilton",
                    "week_date": "2025-02-05",
                    "sentiment": "Positive feedback from Kevin; Good discussion with Sally; Concerns about support issue delays",
                    "opportunity": "AI solution consideration; New hotel chain software transition",
                    "risk": "Support issue delays causing dissatisfaction",
                    "followup": "Sarah to follow up on support issues and create value prop for new hotel chain; Review and add team meeting summary",
                }
            }
        )
    )
