from graphs.customer_insights.tools.insert_ces_tool import add_summary_to_redshift
from graphs.customer_insights.tools.models import AddCustomerEngagementSummaryArgs

data = AddCustomerEngagementSummaryArgs(
    tenant_id="66158fe71bfe10b58cb23eea",
    week_date="2025-03-25 22:07",
    sentiment="sentiment",
    opportunity="opportunity",
    risk="risk",
    followup="followup",
)

if __name__ == "__main__":
    print(add_summary_to_redshift.invoke({"data": data}))
