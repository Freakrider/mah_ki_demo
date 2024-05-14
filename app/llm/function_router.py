from langchain_core.messages import BaseMessage
from langgraph.graph import END

def router(state: list[BaseMessage]):
    """
    Routes the state to the appropriate action based on tool calls.

    Args:
        state (list): The current state of messages.

    Returns:
        str: The next action to take.
    """
    tool_calls = state[-1].additional_kwargs.get("function_call", [])
    return "action" if tool_calls else END
