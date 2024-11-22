import ollama
from Rag import search_similar_chunks
# import os
# import google.generativeai as genai
# from dotenv import load_dotenv
from testRag import get_paragraphs


# Load environment variables
# load_dotenv()
# Configure Google Generative AI
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize an empty list to store chat history temporarily
chat_history = []

def get_ai_response(user_message, chat_history):
    """Generate a response from the AI based on user input and chat history."""
    
    # Define the PDF path and search for relevant chunks
    pdf_path = "./Tamil-Nadu-Startup-and-Innovation-Policy-2023.pdf"
    # data = load_json('./book.json')
    similar_chunks = get_paragraphs(user_message)
    if(similar_chunks):
        return similar_chunks

    similar_chunks = search_similar_chunks(user_message, pdf_path, top_k=3)
    print(similar_chunks)
    
    # Format the chunks into a prompt-friendly format
    similar_chunks_formatted = "\n".join([f"Context {i+1}: {chunk}" for i, chunk in enumerate(similar_chunks)])
    
    # Formulate the prompt to include user message and relevant contexts
    prompt = (
        f"User's Message: {user_message}\n\n"
        f"According to the document:\n{similar_chunks_formatted}\n\n"
        "Based on this information, please provide a detailed response as a paragragh."
    )
    
    # Initialize the response and stream from Ollama model
    response = ""

    stream = ollama.chat(
        model='llama3.2:1b',
        messages=[{'role': 'user', 'content': prompt}],
        stream=True,
    )
    # model = genai.GenerativeModel('gemini-pro')
    # stream = model.generate_content(prompt)
    
    # Collect the response from the stream
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
        response += chunk['message']['content']
        # response += chunk
    
    # Add the AI's response to chat history
    chat_history.append({'user': user_message, 'AI Tutor': response})
    
    return response
