import os
from typing import Annotated
from typing import TypedDict
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from langchain_community.tools.tavily_search import TavilySearchResults


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
llm = ChatAnthropic(model="claude-3-haiku-20240307")


def chatbot(state: State):
    return {"messages": llm.invoke(state["messages"])}


graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

# visualize_graph(graph_builder)


def run_chatbot(messages):
    while True:
        user_input = input("User: ")
        if user_input in ["quit", "exit", "q"]:
            print("Goodbye")
            break

        for event in graph.stream({"messages": ("user", user_input)}):
            for value in event.values():
                print("Assistant", value["messages"].content)


### Adding tools

# Tavily Search

tool = TavilySearchResults(max_results=2)
tools = [tool]
print(tool.invoke("Whats a tool in langgraph"))


### Function calls
