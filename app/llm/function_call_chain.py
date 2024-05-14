from flask import request, jsonify, make_response
import json
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_core.utils.function_calling import convert_to_openai_function
from app.tools.final_answer_tool import final_answer_tool
from app.tools.oersi_search import oersi_search
from app.tools.save_as_txt import save_as_txt
from app.llm.function_mapping import function_mapping

def function_call_chain():
    """
    Endpoint for handling function call chains.
    """
    # WARNING - Not Tested After Refactoring
    print("WARNING - Not Tested After Refactoring")
    data = request.get_json()
    query = data.get("prompt", "")
    if not query:
        return create_response({"error": "No prompt provided"}, 400)

    model = OllamaFunctions(model="llama3", format="json")
    tools = [oersi_search, final_answer_tool, save_as_txt]
    tool_definitions = [convert_to_openai_function(t) for t in tools]
    model_with_function = model.bind_tools(tools=tool_definitions)

    try:
        response = model_with_function.invoke(query)
    except KeyError as e:
        return create_response({"response": f"Error in model invocation: {e} because of user input {query}", "sourceDocuments": []})

    response.pretty_print()

    function_call = response.additional_kwargs.get("function_call")
    if not function_call:
        return create_response({"response": f"'function_call' key is missing in the response additional_kwargs because of user input {query}", "sourceDocuments": []})

    function_name = function_call.get("name")
    arguments = function_call.get("arguments", {})
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            return create_response({"error": "Invalid JSON arguments"}, 400)

    function_result = invoke_function(function_name, arguments)
    return create_response({"response": function_result, "sourceDocuments": []})

def create_response(respObj, status=200):
    """
    Creates a JSON response with a given status code.
    """
    return make_response(jsonify(respObj), status)

def invoke_function(function_name, arguments):
    """
    Invokes the appropriate function based on the function name and arguments.
    """
    if function_name in function_mapping:
        try:
            if 'answer' in arguments:
                return arguments['answer']
            else:
                function = function_mapping[function_name]
                return function.invoke(input=arguments)
        except Exception as e:
            return f"Error invoking function '{function_name}': {str(e)}"
    else:
        return "Function not found in the mapping."
