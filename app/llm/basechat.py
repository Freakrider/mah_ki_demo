from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def llm_call(query):
    """
    Calls the LLM (Language Model) with the given query and returns the result.

    Args:
        query (str): The query to be passed to the LLM.

    Returns:
        str: The result returned by the LLM.
    """
    prompt = ChatPromptTemplate.from_template("{query}")
    model = ChatOpenAI()
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser
    result = chain.invoke({"query": query})
    return result
