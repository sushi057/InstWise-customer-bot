from langchain_openai import ChatOpenAI


def get_openai_model():
    model = ChatOpenAI(model="gpt-4o", temperature=0.5)
    return model
