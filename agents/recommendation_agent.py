from langchain.prompts import ChatPromptTemplate
from models.openai_model import get_openai_model
from tools.tools import recommendation_rag_call, suggest_workaround

recommendation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Recommendation Agent, focused on offering proactive advice and recommendations to the customer."
            "The primary assistant delegates work to you to help user with guidance on how to avoid similar issues in the future. Your tasks include:"
            "Provide recommendations/preventions on how to avoid similar issues in the future based the based on the RAG response."
            "If the issue hasn't been resolved, provide applicable workaround for the issue."
            "Suggest new features or modules that could benefit the user, based on their usage pattern."
            "Provide recommendations for articles, videos, or tutorials related to the user’s context."
            "Your goal is to provide valuable insights that help the user prevent future issues and maximize the benefits of your product."
            "Once the recommendations are provided, signal the Primary Assistant to continue the conversation with the user.",
        ),
        ("placeholder", "{messages}"),
    ]
)

llm = get_openai_model()
recommendation_tools = [recommendation_rag_call, suggest_workaround]

recommendation_runnable = recommendation_prompt | llm.bind_tools(recommendation_tools)
