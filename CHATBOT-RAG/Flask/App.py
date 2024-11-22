from flask import Flask, request, jsonify
from flask_cors import CORS
from rag import get_ai_response

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins (for development)

@app.route('/qa_chat', methods=['POST'])
def qa_chat():
    try:
        user_question = request.json['keyword']
        chat_history = request.json['chat_history']
        # print(f"chat history \n {chat_history}")
        ai_response = get_ai_response(user_question)        
        return jsonify({'answer': ai_response})
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)