from flask import jsonify, make_response, request
from app.tools.oersi_search import oersi_search
from app.llm.basechat import llm_call
from app.llm.agent_system import agent_system
from app.llm.function_call_chain import function_call_chain

def register_routes(app):
    @app.route('/api/plainoersi', methods=['POST'])
    def plainoersi():
        """
        Endpoint for searching OERSI based on a given prompt.
        Returns:
            A JSON response containing the search result.
        """
        data = request.get_json()
        query = data.get("prompt", "")
        if not query:
            return make_response(jsonify({"error": "No prompt provided"}), 400)
        search_result = oersi_search(query)
        return make_response(jsonify(search_result), 200)

    @app.route('/api/basechat', methods=['POST'])
    def basechat():
        """
        Endpoint for base chat LLM call.
        """
        data = request.get_json()
        query = data.get("prompt", "")
        if not query:
            return make_response(jsonify({"error": "No prompt provided"}), 400)
        result = llm_call(query)
        return make_response(jsonify(result), 200)

    @app.route('/api/moodle', methods=['POST'])
    def moodle():
        """
        Endpoint for Moodle LLM call.
        """
        return agent_system()

    @app.route('/api/function', methods=['POST'])
    def function_call():
        """
        Endpoint for function call chain.
        """
        return function_call_chain()
