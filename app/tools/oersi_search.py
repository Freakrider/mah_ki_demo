import requests
from langchain_core.tools import tool
from app.tools.format_oersi_to_markdown import format_oersi_to_markdown

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
