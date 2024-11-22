import google.generativeai as genai
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

# Initialize generative model
model = genai.GenerativeModel("gemini-1.5-flash")


def get_pdf_texts(pdf_docs):
    text = ""
    if pdf_docs:
        pdf_reader = PdfReader(pdf_docs)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible by using the given context.
    Don't provide wrong answers. If you don't know the answer, just say "I don't know".
    Context:\n{context}?\n
    Question:\n{question}\n
    
    Answer:"""
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain


def get_answer_from_pdf(pdf_docs, user_question):
    raw_text = get_pdf_texts(pdf_docs)
    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Check if the FAISS index exists before loading
    if os.path.exists("faiss_index"):
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        chain = get_conversational_chain()
        response = chain(
            {"input_documents": docs, "question": user_question},
            return_only_outputs=True
        )
        return response["output_text"]
    else:
        return "FAISS index not found. Please upload and process the PDF first."


# Example usage of the function:
def get_ai_response(user_question):
    pdf_path = "./Tamil-Nadu-Startup-and-Innovation-Policy-2023.pdf"  # Update with your PDF path
    with open(pdf_path, 'rb') as pdf_file:
        answer = get_answer_from_pdf(pdf_file, user_question)
        print(f"Answer: {answer}")
        return answer