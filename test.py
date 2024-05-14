from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from typing import Annotated, Sequence
from langchain_openai import ChatOpenAI
import functools
from IPython.display import Image, display

# Definition der Werkzeuge und Agenten
def save_as_text(data: Annotated[str, "The data to save as text."]):
    with open("results.txt", "w") as file:
        file.write(data)
    return "Data saved successfully."

def research_query(prompt: Annotated[str, "The search prompt for OERSI API."]):
    return {"name": "Research Example", "description": "A detailed description based on " + prompt, "keywords": ["keyword1", "keyword2"]}

# Agent-Funktionen
def create_agent(llm, tools, system_message: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant, collaborating with other assistants. Use the provided tools to progress towards answering the question."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)

# Einrichtung der Umgebung und Agenten
llm = ChatOpenAI(model="gpt-4-1106-preview")
research_agent = create_agent(llm, [research_query], "Conduct research using provided prompt.")
presenter_agent = create_agent(llm, [save_as_text], "Save the research results into a text file.")

# Definition des Graphen
workflow = StateGraph()
workflow.add_node("Researcher", functools.partial(agent_node, agent=research_agent, name="Researcher"))
workflow.add_node("Presenter", functools.partial(agent_node, agent=presenter_agent, name="Presenter"))
workflow.add_conditional_edges("Researcher", lambda x: "Presenter", {"continue": "Presenter"})
workflow.add_conditional_edges("Presenter", lambda x: "__end__", {"continue": END})
workflow.set_entry_point("Researcher")

# Ausführen und Darstellen des Graphen
graph = workflow.compile()
try:
    display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
except:
    pass