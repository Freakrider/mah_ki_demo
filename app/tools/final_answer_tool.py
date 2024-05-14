from langchain_core.tools import tool

@tool("final_answer")
def final_answer_tool(answer: str, source: str):
    """
    Returns a natural language response to the user in `answer`, and a
    `source` which provides citations for where this information came from.
    Use it if no other tool is applicable.

    Args:
        answer (str): The answer to be returned.
        source (str): The source of the information.

    Returns:
        str: The answer with the source.
    """
    return ""
