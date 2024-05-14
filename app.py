from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from langchain_core.messages import HumanMessage

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from tools import oersi_search
from graph import create_workflow, stream_graph
from IPython.display import Image, display

import getpass
import os
from dotenv import load_dotenv
load_dotenv()

import requests
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
def llmCall2(query):
    data = request.get_json()
    query = data["prompt"]

    from langchain_experimental.llms.ollama_functions import OllamaFunctions
    from langchain_core.utils.function_calling import convert_to_openai_function

    from tools import final_answer_tool,oersi_search, save_as_txt

    model = OllamaFunctions(
        model="llama3", 
        format="json"
        )

    tools = [oersi_search, final_answer_tool, save_as_txt]
    tool_definitions = [convert_to_openai_function(t) for t in tools]
    model.bind_tools
    model = model.bind_tools(
        tools=tool_definitions
    )

    # Dictionary mapping function names to their corresponding functions
    function_mapping = {
        "final_answer": final_answer_tool,
        "save_as_txt": save_as_txt,
        "oersi_search": oersi_search
    }

    response = model.invoke(query)

    import json

    # Extract the function name and arguments from the response
    function_call = response.additional_kwargs.get("function_call")
    function_name = function_call.get("name")
    arguments = function_call.get("arguments")

    # Convert arguments to a dictionary if it's a string
    if isinstance(arguments, str):
        arguments = json.loads(arguments)

    # Check if the function name exists in the mapping
    if function_name in function_mapping:
        # If 'answer' is in arguments, just print 'answer'
        if 'answer' in arguments:
            function_result = model(arguments['answer'])
        else:
            # Call the corresponding function with the arguments
            function = function_mapping[function_name]
            function_result = function.invoke(input = arguments)
    else:
        function_result = "Function not found in the mapping."

    # Print the user response
    print(function_result)
    respObj = {"response": function_result, "sourceDocuments": []}
    response = make_response(jsonify(respObj), 200)
    return response

    


@app.route('/api/agent', methods=['POST'])
def agent_system(query):#todo query raus
    # data = request.get_json()
    # query = data["prompt"]

    graph = create_workflow()
    display_graph(graph)
    inputs ={"messages": [HumanMessage(content=query)]}
    output = stream_graph(graph, inputs)

    return output

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
    app.run(debug=FLASK_DEBUG, ssl_context='adhoc')
