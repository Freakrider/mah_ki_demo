import json
import logging
from app.llm.function_mapping import function_mapping

logger = logging.getLogger(__name__)

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
            logger.error(f"Error invoking function '{function_name}': {e}")
            return f"Error invoking function '{function_name}': {str(e)}"
    else:
        logger.error("Function not found in the mapping")
        return "Function not found in the mapping."
