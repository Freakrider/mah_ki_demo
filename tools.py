import os
import requests
from langchain_core.tools import tool

@tool("oersi_search")
def oersi_search(prompt):
    """
    Perform a search on the OERSI API based on the given prompt for the Fields name, description, and keywords.

    Args:
        prompt (str): The search prompt. This can be a keyword, phrase, or sentence to search for.
    Returns:
        dict: The JSON response from the API if the request is successful.
              Otherwise, a dictionary containing an error message and the status code.

    """

    print("Performing search on OERSI API " + prompt)
    url = 'https://oersi.org/resources/api/search/oer_data/_search?pretty'
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }

    query = {
        "multi_match": {
            "query": prompt,
            "fields": ["name^3", "description^2", "keywords"],
            "type": "best_fields"
        }
    }

    # Adding filters
    # Filters are not working properly
    filters = []
    # if language:
    #     filters.append({"term": {"inLanguage.keyword": language}})
    # if from_date and to_date:
    #     filters.append({
    #         "range": {
    #             "datePublished": {
    #                 "gte": from_date,
    #                 "lte": to_date
    #             }
    #         }
    #     })

    # if filters:
    #     query = {
    #         "bool": {
    #             "must": query,
    #             "filter": filters
    #         }
    #     }

    data = {
        "size": 5,
        "from": 0,
        "query": query,
        "sort": [{"datePublished": "desc"}]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("API request successful")
        raw_results = response.json()
        structured_results = []
        
        for hit in raw_results.get('hits', {}).get('hits', []):
            source = hit.get('_source', {})
            structured_results.append({
                'name': source.get('name', 'No name available'),
                'description': source.get('description', 'No description available'),
                'keywords': source.get('keywords', []),
                'creator': [creator.get('name', 'Unknown') for creator in source.get('creator', [])],
                'inLanguage': source.get('inLanguage', ['Unknown']),
                'datePublished': source.get('datePublished', 'Unknown'),
                'isAccessibleForFree': source.get('isAccessibleForFree', False),
                'license': source.get('license', {}).get('id', 'No license information'),
                'url': source.get('id', 'No URL available')
            })
        
        return format_oersi_to_markdown(structured_results)
    else:
        return format_oersi_to_markdown({"error": "API request failed", "status_code": response.status_code})
    
def format_oersi_to_markdown(results):
    """
    Convert a list of structured search results or an error message into a Markdown formatted string.

    Args:
        results (list or dict): A list of dictionaries containing the structured search results or a dictionary containing an error message.
    
    Returns:
        str: A string containing the formatted Markdown.
    """
    if isinstance(results, dict) and "error" in results:
        markdown = f"## Error\n\n**Message:** {results['error']}\n\n**Status Code:** {results['status_code']}\n\n"
    else:
        markdown = ""
        
        for result in results:
            name = result.get('name', 'No name available')
            description = result.get('description', 'No description available')
            keywords = ", ".join(result.get('keywords', [])) if result.get('keywords') else "No keywords available"
            creators = ", ".join(result.get('creator', ['Unknown'])) if result.get('creator') else "Unknown"
            languages = ", ".join(result.get('inLanguage', ['Unknown'])) if result.get('inLanguage') else "Unknown"
            date_published = result.get('datePublished', 'Unknown')
            is_free = "Yes" if result.get('isAccessibleForFree', False) else "No"
            license_info = result.get('license', 'No license information')
            url = result.get('url', 'No URL available')

            markdown += f"## {name}\n\n"
            markdown += f"**Description:** {description}\n\n"
            markdown += f"**Keywords:** {keywords}\n\n"
            markdown += f"**Creators:** {creators}\n\n"
            markdown += f"**Languages:** {languages}\n\n"
            markdown += f"**Date Published:** {date_published}\n\n"
            markdown += f"**Accessible for Free:** {is_free}\n\n"
            markdown += f"**License:** [{license_info}]({license_info})\n\n"
            markdown += f"**URL:** [{url}]({url})\n\n"
            markdown += "---\n\n"
    
    return markdown
    
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