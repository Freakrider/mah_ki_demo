import os
import requests
from langchain_core.tools import tool

@tool("oersi_search")
def oersi_search(prompt ):
    """
    Perform a search on the OERSI API based on the given prompt for the Fields name, description, and keywords.

    Args:
        prompt (str): The search prompt. This can be a keyword, phrase, or sentence to search for.
    Returns:
        dict: The JSON response from the API if the request is successful.
              Otherwise, a dictionary containing an error message and the status code.

    """

    print("Performing search on OERSI API "+prompt)
    url = 'https://oersi.org/resources/api/search/oer_data/_search?pretty'
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }

    data = {
        "size": 5,
        "from": 0,
        "query": {
            "multi_match": {
                "query": prompt,
                "fields": ["name", "description", "keywords"]
            }
        },
        "sort": [{"id": "asc"}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("API request successful")
        return response.json()  
    else:
        return {"error": "API request failed", "status_code": response.status_code}

@tool("final_answer")
def final_answer_tool(
    answer: str,
    source: str
):
    """Returns a natural language response to the user in `answer`, and a
    `source` which provides citations for where this information came from.
    """
    return ""

@tool("save_as_txt")
def save_as_txt(title="", data=""):
    """
    Save the given data as a text file with the specified title.

    Parameters:
    - title (str): The title of the text file.
    - data (str): The data to be written to the text file.

    Returns:
    None
    """
    folder_path = "output"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(f"{folder_path}/{title}.txt", "w") as file:
        file.write(data)

    return "Data saved successfully."