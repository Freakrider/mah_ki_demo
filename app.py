from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tools import oersi_search
from graph import create_workflow, stream_graph
from IPython.display import Image, display
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_core.utils.function_calling import convert_to_openai_function

from tools import final_answer_tool, oersi_search, save_as_txt

import os
from dotenv import load_dotenv
load_dotenv()

# Umgebungsvariablen für die Konfiguration
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1']

app = Flask(__name__, static_folder='dist', template_folder='dist')
CORS(app, supports_credentials=True)

@app.route('/api/plainoersi', methods=['POST'])
def plainoersi():
    data = request.get_json()
    query = data["prompt"]
    search_result = oersi_search(query)
    response = make_response(jsonify(search_result), 200)
    return response

@app.route('/api/basechat', methods=['POST'])
def llmCall(query):
    """
    Calls the LLM (Language Model) with the given query and returns the result.

    Args:
        query (str): The query to be passed to the LLM.

    Returns:
        str: The result returned by the LLM.

    """
    prompt = ChatPromptTemplate.from_template("{query}")
    
    model = ChatOpenAI() 
    #If you want to use a local API, you can use the following code with something like lm Studio or ollama: 
    #ChatOpenAI(base_url="http://localhost:1234/v1",temperature=0, api_key="not-needed")
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    result = chain.invoke({"query": query})
    return result

@app.route('/api/moodle', methods=['POST'])
def agent_system():
    data = request.get_json()
    print(data)
    query = data["prompt"]

    model = OllamaFunctions(
        model="llama3", 
        format="json"
    )

    tools = [oersi_search, final_answer_tool, save_as_txt]
    tool_definitions = [convert_to_openai_function(t) for t in tools]
    model_with_function = model.bind_tools(
        tools=tool_definitions
    )

    from langchain_openai import ChatOpenAI
    from langchain_core.messages import BaseMessage, HumanMessage
    from langgraph.graph import END, MessageGraph

    graph = MessageGraph()

    graph.add_node("supervisor", model_with_function)

    from langgraph.prebuilt import ToolNode
    tool_node = ToolNode([final_answer_tool, oersi_search, save_as_txt])
    graph.add_node("action", tool_node)
    graph.add_edge("action", END)


    graph.set_entry_point("supervisor")

    from typing import Literal

    def router(state: list[BaseMessage]):
        tool_calls = state[-1].additional_kwargs.get("function_call", [])
        if len(tool_calls):
            return "action"
        else:
            return END


    graph.add_conditional_edges("supervisor", router)
    runnable = graph.compile()
    display_graph(runnable)



    # Dictionary mapping function names to their corresponding functions
    function_mapping = {
        "final_answer": final_answer_tool,
        "save_as_txt": save_as_txt,
        "oersi_search": oersi_search
    }

    try:
        response = runnable.invoke(query)[-1]
    except KeyError as e:
        respObj = {"response": f"Error in model invocation: {e} because of userinput {query}", "sourceDocuments": []}
        response = make_response(jsonify(respObj), 200)
        return response

    import json


    # Check if the 'tool' key exists before accessing it
    if "function_call" in response.additional_kwargs:
        function_call = response.additional_kwargs["function_call"]
    else:
        print("'function_call' key is missing in the response.additional_kwargs")
        respObj = {"response": f"'function_call' key is missing in the response.additional_kwargs because of userinput {query}", "sourceDocuments": []}
        response = make_response(jsonify(respObj), 200)
        return response

    # Extract the function name and arguments from the response
    function_name = function_call.get("name")
    arguments = function_call.get("arguments", {})

    # Print the user response
    print(function_call)
    print("_------------------_")
    print(arguments)

    # Convert arguments to a dictionary if it's a string
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return make_response(jsonify({"error": "Invalid JSON arguments"}), 400)

    # Check if the function name exists in the mapping
    if function_name in function_mapping:
        try:
            # If 'answer' is in arguments, just print 'answer'
            if 'answer' in arguments:
                function_result = arguments['answer']
            else:
                # Call the corresponding function with the arguments
                function = function_mapping[function_name]
                function_result = function.invoke(input=arguments)
        except Exception as e:
            print(f"Error invoking function '{function_name}': {e}")
            function_result = f"Error invoking function '{function_name}': {str(e)}"
    else:
        function_result = "Function not found in the mapping."

    print("_------------------_")
    print(function_result)

    respObj = {"response": function_result, "sourceDocuments": []}
    response = make_response(jsonify(respObj), 200)
    return response


@app.route('/api/function', methods=['POST'])
def function_call_chain():
    data = request.get_json()
    print(data)
    query = data["prompt"]

    from langchain_experimental.llms.ollama_functions import OllamaFunctions
    from langchain_core.utils.function_calling import convert_to_openai_function

    from tools import final_answer_tool, oersi_search, save_as_txt

    model = OllamaFunctions(
        model="llama3", 
        format="json"
    )

    tools = [oersi_search, final_answer_tool, save_as_txt]
    tool_definitions = [convert_to_openai_function(t) for t in tools]
    model_with_function = model.bind_tools(
        tools=tool_definitions
    )

    # Dictionary mapping function names to their corresponding functions
    function_mapping = {
        "final_answer": final_answer_tool,
        "save_as_txt": save_as_txt,
        "oersi_search": oersi_search
    }

    try:
        response = model_with_function.invoke(query)
    except KeyError as e:
        respObj = {"response": f"Error in model invocation: {e} because of userinput {query}", "sourceDocuments": []}
        response = make_response(jsonify(respObj), 200)
        return response

    import json
    response.pretty_print()

    # Check if the 'tool' key exists before accessing it
    if "function_call" in response.additional_kwargs:
        function_call = response.additional_kwargs["function_call"]
    else:
        print("'function_call' key is missing in the response.additional_kwargs")
        respObj = {"response": f"'function_call' key is missing in the response.additional_kwargs because of userinput {query}", "sourceDocuments": []}
        response = make_response(jsonify(respObj), 200)
        return response

    # Extract the function name and arguments from the response
    function_name = function_call.get("name")
    arguments = function_call.get("arguments", {})

    # Print the user response
    print(function_call)
    print("_------------------_")
    print(arguments)

    # Convert arguments to a dictionary if it's a string
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return make_response(jsonify({"error": "Invalid JSON arguments"}), 400)

    # Check if the function name exists in the mapping
    if function_name in function_mapping:
        try:
            # If 'answer' is in arguments, just print 'answer'
            if 'answer' in arguments:
                function_result = arguments['answer']
            else:
                # Call the corresponding function with the arguments
                function = function_mapping[function_name]
                function_result = function.invoke(input=arguments)
        except Exception as e:
            print(f"Error invoking function '{function_name}': {e}")
            function_result = f"Error invoking function '{function_name}': {str(e)}"
    else:
        function_result = "Function not found in the mapping."

    print("_------------------_")
    print(function_result)

    respObj = {"response": function_result, "sourceDocuments": []}
    response = make_response(jsonify(respObj), 200)
    return response


def display_graph(graph):
    graph_image_path = os.path.join("output", "graph_visualization.png")
    try:
        graph_image = graph.get_graph(xray=True).draw_mermaid_png()
        with open(graph_image_path, "wb") as f:
            f.write(graph_image)
        display(Image(graph_image))  # Anzeigen des Graphen im Jupyter Notebook
        print(f"Graph visualized and saved as PNG at '{graph_image_path}'")
    except Exception as e:
        print(f"Failed to create or display graph: {e}")

if __name__ == '__main__':
    # res = agent_system("Call Oersi and search for Generative KI.")
    # print(res)
    app.run(debug=FLASK_DEBUG)
    # , ssl_context='adhoc'
