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

# response = model.invoke("3+4=?")
# print(response)
# # content='' 
# # additional_kwargs={'function_call': {'name': 'final_answer', 'arguments': '{"answer": "7", "source": "Basic arithmetic operation"}'}} 
# # id='run-c3d4bdcb-ff1d-4fcb-b8af-efa1b35e5338-0'

# response = model.invoke("Speiche Hello World in eine Text Datei.")
# print(response)
# # content='' 
# # additional_kwargs={'function_call': {'name': 'save_as_txt', 'arguments': '{"title": "", "data": "Hello World"}'}} 
# # id='run-afdfe768-3336-49a6-9910-1c576ae9dd38-0'

# response = model.invoke("Oersi Suche nach Generative KI.")
# # print(response)
# # content=''
# # additional_kwargs={'function_call': {'name': 'oersi_search', 'arguments': '{"prompt": "Generative KI"}'}}
# # id='run-8aec78c0-a540-4447-b594-d9d249f4a080-0'


# Dictionary mapping function names to their corresponding functions
function_mapping = {
    "final_answer": final_answer_tool,
    "save_as_txt": save_as_txt,
    "oersi_search": oersi_search
}

# Example response
# response = model.invoke("Oersi Suche nach Generative KI.")
response = model.invoke("Call Oersi and search for Generative KI.")

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
