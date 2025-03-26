from graphs.customer_insights.tools.insert_ces_tool import insert_into_redshift
from graphs.customer_insights.tools.models import AddCustomerEngagementSummaryArgs

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
    print(insert_into_redshift.invoke({"data": data}))
