import os
from langchain_core.tools import tool

@tool("save_as_txt")
def save_as_txt(title="", data=""):
    """
    Save the given data as a text file with the specified title.

    Args:
        title (str): The title of the text file.
        data (str): The data to be written to the text file.

    Returns:
        str: Confirmation message.
    """
    folder_path = "output"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(f"{folder_path}/{title}.txt", "w") as file:
        file.write(data)

    return "Data saved successfully."
