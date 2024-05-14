from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_core.utils.function_calling import convert_to_openai_function
from langgraph.graph import END, MessageGraph
from langgraph.prebuilt import ToolNode
from app.llm.function_router import router

def create_message_graph(tools):
    """
    Creates and configures a MessageGraph with the given tools.

    Args:
        tools (list): A list of tools to be used in the MessageGraph.

    Returns:
        MessageGraph: The configured MessageGraph.
    """
    tool_definitions = [convert_to_openai_function(t) for t in tools]
    model_with_function = OllamaFunctions(model="llama3", format="json").bind_tools(tools=tool_definitions)

    graph = MessageGraph()
    graph.add_node("supervisor", model_with_function)
    tool_node = ToolNode(tools)
    graph.add_node("action", tool_node)
    graph.add_edge("action", END)
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", router)

    return graph
