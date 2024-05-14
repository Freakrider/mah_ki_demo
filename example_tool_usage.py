from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_core.utils.function_calling import convert_to_openai_function

from tools import final_answer_tool,oersi_search, save_as_txt

model = OllamaFunctions(
    model="llama3", 
    format="json"
    )

tools = [oersi_search, final_answer_tool, save_as_txt]
tool_definitions = [convert_to_openai_function(t) for t in tools]
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


import json

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, MessageGraph
from langgraph.prebuilt.tool_node import ToolNode


# Define the function that determines whether to continue or not
def should_continue(messages):
    last_message = messages[-1]
    # If there is no function call, then we finish
    if not last_message.additional_kwargs.get("function_call"):
        return END
    else:
        return "action"

# Define a new graph
workflow = MessageGraph()

workflow.add_node("agent", model)
workflow.add_node("action", ToolNode(tools))
# Research agent and node
research_agent = create_agent(
    llm,
    [tavily_tool],
    system_message="You should provide accurate data for the chart_generator to use.",
)
research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")



workflow.set_entry_point("agent")

# Conditional agent -> action OR agent -> END
workflow.add_conditional_edges(
    "agent",
    should_continue,
)

# Always transition `action` -> `agent`
workflow.add_edge("action", "agent")

app = workflow.compile()
# Run the graph
thread = {"configurable": {"thread_id": "4"}}
for event in app.stream("what is the weather in sf currently", thread):
    for v in event.values():
        print(v)
# from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
# chain = model | JsonOutputFunctionsParser
# resp = chain.invoke("Research nach Generative KI")
# print(resp)
# from langchain_core.messages import HumanMessage
# from langgraph.graph import END, MessageGraph
# from langgraph.prebuilt import ToolNode
# builder = MessageGraph()

# builder.add_node("oracle", model)

# tool_node = ToolNode([oersi_search, final_answer_tool, save_as_txt])
# builder.add_node("multiply", tool_node)

# builder.add_edge("multiply", END)

# builder.set_entry_point("oracle")

# from typing import Literal
# from langchain_core.messages import HumanMessage, BaseMessage
# from typing import Dict, Sequence, TypedDict, Annotated, List, Union


# def router(state: List[BaseMessage]) -> Literal["multiply", "__end__"]:
#     tool_calls = state[-1].additional_kwargs.get("function_call", [])
#     if len(tool_calls):
#         return "multiply"
#     else:
#         return "__end__"

# builder.add_conditional_edges("oracle", router)
# runnable = builder.compile()

# print(runnable.invoke(HumanMessage("Speiche Hello World in eine Text Datei.")))


# from langchain.agents import AgentExecutor, create_tool_calling_agent
# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.agents import AgentExecutor, create_tool_calling_agent

# # Get the prompt to use - can be replaced with any prompt that includes variables "agent_scratchpad" and "input"!
# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful assistant.",
#         ),
#         ("placeholder", "{chat_history}"),
#         ("human", "{input}"),
#         ("placeholder", "{agent_scratchpad}"),
#     ]
# )

# # prompt.pretty_print()

# # Construct the Tools agent


# #agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
# #agent_executor.invoke({"input": "what is LangChain?"})