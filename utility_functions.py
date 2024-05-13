from typing import Dict, Any
from langchain_core.messages import HumanMessage
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def validate_state(state: Dict[str, Any]) -> None:
    if "next" not in state or not isinstance(state["next"], str):
        raise ValueError("State must have a 'next' key with string value.")
    if "messages" not in state or not isinstance(state["messages"], list):
        raise ValueError("State must have a 'messages' key with list of messages.")

def stream_graph(graph, inputs: Any) -> Any:
    try:
        # for output in graph.stream(inputs, {"recursion_limit": 100}):
        #     print("Output received:", output)
        #     for key, value in output.items():
        #         print(f"Finished running: {key}: {value}")
        #         if isinstance(value, dict) and "generation" in value:
        #             print(value["generation"])
        #         else:
        #             print("Unexpected value type or structure:", value)
        output = graph.invoke(inputs, {"recursion_limit": 100})
    except Exception as e:
        print("Error encountered during streaming:", e)
        raise e
    return output

def agent_node(state, agent, name):
    # Debugging: Eingehenden State ausgeben
    print(f"Entering {name} node with state:", state)

     # Validierung: Überprüfen, ob 'messages' im State vorhanden ist
    if 'messages' not in state or not isinstance(state['messages'], list):
        raise ValueError(f"Expected 'messages' key in state with a list of messages, got {state.get('messages')}")

     # Agenten aufrufen und das Ergebnis erhalten
    result = agent.invoke(state)

    # Debugging
    print(f"Exiting {name} node with result:", result)

    return {"messages": [HumanMessage(content=result["output"], name=name)]}

def create_agent(llm: OllamaFunctions, tools: list, system_prompt: str):
    # Each worker node will be given a name and some tools.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor
