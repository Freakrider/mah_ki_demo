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
