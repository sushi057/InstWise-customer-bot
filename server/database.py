import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from motor import motor_asyncio

load_dotenv()

client = motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URI"])
database = client.AIChatbot
customer_collection = database.get_collection("customers")
feedback_collection = database.get_collection("feedback")
# helpers


def customer_helper(customer) -> dict:
    return {
        "id": str(customer["_id"]),
        "name": customer["name"],
        "email": customer["email"],
        "arr": customer["arr"],
        "licenses_purchased": customer["licenses_purchased"],
        "licenses_used": customer["licenses_used"],
        "renewal_date": customer["renewal_date"],
        "csm_agent": customer["csm_agent"],
        "account_executive": customer["account_executive"],
        "health_score": customer["health_score"],
        "login_count": customer["login_count"],
        "main_feature_usage_count": customer["main_feature_usage_count"],
        "total_ticket_count": customer["total_ticket_count"],
        "open_ticket_count": customer["open_ticket_count"],
        "escalated_ticket": customer["escalated_ticket"],
        "closed_ticket_count": customer["closed_ticket_count"],
        "organization": customer["organization"],
        "created_at": customer["createdAt"],
        "updated_at": customer["updatedAt"],
    }


def feedback_helper(feedback) -> dict:
    return {
        "customer_id": feedback["customer_id"],
        "feedback": feedback["feedback"],
        "rating": feedback["rating"],
    }


async def retrieve_customers():
    customers = []
    async for customer in customer_collection.find():
        customers.append(customer_helper(customer))
    return customers


async def retrieve_customer(id: str) -> dict:
    customer = await customer_collection.find_one({"_id": id})
    if customer:
        return customer_helper(customer)
    return None


async def retrieve_customer_by_email(email: str):
    customer = await customer_collection.find_one({"email": email})
    if customer:
        return customer_helper(customer)
    return None


async def add_feedback(feedback_data: dict) -> dict:
    feedback = await feedback_collection.insert_one(feedback_data)
    new_feedback = await feedback_collection.find_one({"_id": feedback.inserted_id})
    return feedback_helper(new_feedback)
