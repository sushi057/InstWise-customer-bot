from langchain_core.tools import tool


@tool
def ToSolutionAgent():
    """
    Transfer work to the solution agent to handle the RAG call and suggest a workaround.
    """
    return


@tool
def ToFollowUpAgent():
    """
    Transfer work to the follow-up agent to handle the personalized follow-up.
    """
    return


@tool
def CompleteOrEscalate():
    """
    Indicate that the tasks for this agent are completed and go to Primary Assistant
    """
    return
