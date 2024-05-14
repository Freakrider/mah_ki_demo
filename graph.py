from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder,PromptTemplate
from langchain_openai import ChatOpenAI
from langchain import hub
from langgraph.graph import StateGraph, END
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_core.agents import AgentAction, AgentFinish
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.agents import create_tool_calling_agent
from langchain.agents import create_openai_tools_agent

from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents import AgentExecutor

from langchain_core.messages import HumanMessage, BaseMessage
from utility_functions import validate_state, stream_graph,agent_node,create_agent
from typing import Dict, List, Sequence, TypedDict, Annotated, List, Union
from tools import final_answer_tool, oersi_search, save_as_txt
import functools
import operator

class AgentState(TypedDict):
    input: str
    agent_out: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]

def create_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)
    additional_members = ["Researcher","Presenter"]

    model = OllamaFunctions(model="llama3", format="json")#ChatOpenAI( model_name="llama3:instruct", openai_api_base="http://localhost:11434/v1",temperature=0, api_key="llama3:instruct")#OllamaFunctions(model="llama3:instruct", format="json", temperature=0)
    options = ["FINISH"] + additional_members

    supervisor_template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a supervisor tasked with managing a conversation between the following workers: "Researcher", "Presenter" and the user.

    Use the following criteria to decide how to route between the workers or respond to the user: \n\n

    1. If the prompt is search related, route to the Researcher, choose "oersi_search".
    2. If the prompt is save related, route to the Presenter, choose "final_answer_tool".
    3. If the prompt is not related to either, choose "FINISH" to end the conversation.

    Just type the name of the worker you want to act next or "FINISH" to end the conversation.
    Example: "oersi_search" or "final_answer_tool" or "FINISH"
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    {input}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", supervisor_template),
        MessagesPlaceholder(variable_name="input"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
        (
            "system",
            "Given the conversation above, who should act next?"
            " Or should we FINISH? Select one of: {options}",
        ),
    ]).partial(options=str(options), additional_members=", ".join(additional_members))

    # supervisor_chain = (
    #     prompt
    #     | model
    #     | JsonOutputFunctionsParser()
    # )

    # supervisor_chain = supervisor_prompt | model | JsonOutputParser()

    # sub_prompt = hub.pull("hwchase17/openai-functions-agent")
    query_agent_runnable = create_openai_tools_agent(
    llm=model,
    tools=[final_answer_tool, oersi_search],
    prompt=prompt
    )
    
    inputs = {
    "input": "Call Oersi and search for Generative KI.",
    "intermediate_steps": []
}
    agent_out = query_agent_runnable.invoke(inputs)
    print(agent_out)

    # print(supervisor_chain.invoke({"messages": [HumanMessage(content="Call Oersi and search for Moodle.")]}))

#     research_agent = create_agent(model, [oersi_search], "You are a oersi researcher.")
#     research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")


#     present_agent = create_agent(
#         model,
#         [save_as_txt],
#         "You are a presenter. You can save text as a text file.",
#     )
#     present_node = functools.partial(agent_node, agent=present_agent, name="Presenter")

#     workflow.add_node("Researcher", research_node)
#     workflow.add_node("Presenter", present_node)
#     workflow.add_node("Supervisor", supervisor_chain)

#     for member in additional_members:
#         workflow.add_edge(member, "Supervisor")

#     conditional_map = {k: k for k in additional_members}
#     conditional_map["FINISH"] = END
#     workflow.add_conditional_edges("Supervisor", lambda x: x["next"], conditional_map)

#     # workflow.add_conditional_edges(
#     #     "Supervisor",
#     #     lambda x: x["next"],
#     #     {
#     #         "Reseacher": "Researcher",
#     #         "Presenter": "Presenter",
#     #         "FINISH": END
#     #     },
# #)

#     workflow.set_entry_point("Supervisor")


    # res = supervisor_chain.invoke({"messages": [HumanMessage(content="Call Oersi and search for Moodle.")]})
    # print(res)
    res= workflow.compile()
    return res
