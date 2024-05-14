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
    res = agent_system("Call Oersi and search for Generative KI.")
    print(res)
    app.run(debug=FLASK_DEBUG, ssl_context='adhoc')
