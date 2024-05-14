from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

import json

from langchain_core.messages import ToolMessage
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_core.utils.function_calling import convert_to_openai_function

from tools import final_answer_tool,oersi_search, save_as_txt


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)



model = OllamaFunctions(
    model="llama3", 
    format="json"
    )
tools = [oersi_search, final_answer_tool, save_as_txt]
tool_definitions = [convert_to_openai_function(t) for t in tools]
model.bind_tools
model = model.bind_tools(
    #Same as: tools=tool_definitions
    tools=[
        {
            "name": oersi_search.name,
            "description": oersi_search.description,
            "parameters": oersi_search.args,
        },
        {
            "name": final_answer_tool.name,
            "description": final_answer_tool.description,
            "parameters": final_answer_tool.args,
        },
        {
            "name": save_as_txt.name,
            "description": save_as_txt.description,
            "parameters": save_as_txt.args,
        }
    ],
)


def chatbot(state: State):
    return {"messages": [model.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")

class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        
        outputs = []
        print(message)

        #TODO SAUBER machen 
        function_call = message.additional_kwargs.get("function_call", [])


        function_name = function_call.get("name")
        arguments = function_call.get("arguments")

            # Convert arguments to a dictionary if it's a string
        if isinstance(arguments, str):
            arguments = json.loads(arguments)

        if function_name in self.tools_by_name:
            tool_result = self.tools_by_name[function_name].invoke(arguments)
            outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=function_name,
                        tool_call_id=message.id,
                    )
                )
        else:
            raise ValueError(f"Function {function_name} not found in tools_by_name")
        
        return {"messages": outputs}


tool_node = BasicToolNode(tools=tools)
graph_builder.add_node("action", tool_node)
graph_builder.add_edge("action", "chatbot")


from typing import Literal


def route_tools(
    state: State,
) -> Literal["action", "__end__"]:
    """Use in the conditional_edge to route to the ToolNode if the last message

    has tool calls. Otherwise, route to the end."""
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "additional_kwargs"):
        return "action"
    return "__end__"


# The `tools_condition` function returns "action" if the chatbot asks to use a tool, and "__end__" if
# it is fine directly responding. This conditional routing defines the main agent loop.
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you
    # want to use a node named something else apart from "action",
    # You can update the value of the dictionary to something else
    # e.g., "action": "my_tools"
    {"action": "action", "__end__": "__end__"},
)

graph = graph_builder.compile()

for event in graph.stream({"messages": ("user", "Speicher eine Datei mit dem Inhalt Hello World.")}):
    for value in event.values():
        print("Assistant:", value["messages"][-1])