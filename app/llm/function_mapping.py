from app.tools.final_answer_tool import final_answer_tool
from app.tools.oersi_search import oersi_search
from app.tools.save_as_txt import save_as_txt

function_mapping = {
    "final_answer": final_answer_tool,
    "save_as_txt": save_as_txt,
    "oersi_search": oersi_search
}
