from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser

from langchain_experimental.llms.ollama_functions import OllamaFunctions

from langchain_core.messages import HumanMessage, BaseMessage
from utility_functions import validate_state, stream_graph,agent_node,create_agent
from typing import Dict, List, Sequence, TypedDict, Annotated
from tools import return_text, oersiSearch, save_as_txt
import functools
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

def create_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)
    additional_members = ["Researcher","Presenter"]

    model = OllamaFunctions(model="llama3", format="json")
    options = ["FINISH"] + additional_members

    route_tool = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                }
            },
            "required": ["next"],
        },
    }

    model = model.bind_tools(tools=[route_tool], function_call={"name": "route"})

    # system_prompt = (
    #     "You are a supervisor tasked with managing a conversation between the"
    #     " following workers: {additional_members}. Given the following user request,"
    #     " respond with the worker to act next. Each worker will perform a"
    #     " task and respond with their results and status. When finished,"
    #     " respond with FINISH."
    # )

    system_prompt = """
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a supervisor tasked with managing a conversation between the following workers: {additional_members}.
    Given the following user request, respond with the worker to act next.
    Each worker will perform a task and respond with their results and status. When finished, respond with FINISH.
    <|start_header_id|>assistant<|end_header_id|>
    """.strip()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Given the conversation above, who should act next?"
            " Or should we FINISH? Select one of: {options}",
        ),
    ]).partial(options=str(options), additional_members=", ".join(additional_members))

    supervisor_chain = (
        prompt
        | model
        | JsonOutputFunctionsParser()
    )

    research_agent = create_agent(model, [oersiSearch], "You are a oersi researcher.")
    research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")


    present_agent = create_agent(
        model,
        [save_as_txt],
        "You are a presenter. You can save text as a text file.",
    )
    present_node = functools.partial(agent_node, agent=present_agent, name="Presenter")


    workflow.add_node("Researcher", research_node)
    workflow.add_node("Presenter", present_node)
    workflow.add_node("Supervisor", supervisor_chain)

    for member in additional_members:
        workflow.add_edge(member, "Supervisor")

    conditional_map = {k: k for k in additional_members}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges("Supervisor", lambda x: x["next"], conditional_map)
    workflow.set_entry_point("Supervisor")


    # res = supervisor_chain.invoke({"messages": [HumanMessage(content="Call Oersi and search for Moodle.")]})
    # print(res)
    res= workflow.compile()
    return res
