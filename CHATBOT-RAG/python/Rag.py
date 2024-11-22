import re
import fitz  # PyMuPDF to extract text from PDFs
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

# 1. Extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text

# 2. Chunk text based on sentences and size limit
def chunk_text(text, chunk_size=500):
    # Regular expression to split text into sentences
    sentence_endings = re.compile(r'([.!?])\s*')  # Split at sentence-ending punctuation marks
    sentences = sentence_endings.split(text)  # Split into sentences
    
    # Recombine sentences into chunks
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence.strip() + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence.strip() + " "
    
    # Add the last chunk if exists
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# 3. Initialize Sentence Transformer and FAISS
def create_faiss_index(chunks):
    # Load pre-trained model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Convert chunks to embeddings
    embeddings = model.encode(chunks)
    
    # Normalize the embeddings (important for FAISS)
    embeddings = normalize(embeddings)
    
    # Initialize FAISS index
    dim = embeddings.shape[1]  # Get dimension of embeddings
    index = faiss.IndexFlatL2(dim)  # L2 distance for similarity search
    index.add(embeddings)  # Add embeddings to the FAISS index
    
    return index, model

# 4. Function to search for most similar chunks
def search_similar_chunks(query, pdf_path, top_k=3):
    # Step 1: Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Step 2: Chunk the text into manageable pieces (e.g., paragraphs, sentences)
    chunks = chunk_text(text)

    # Step 3: Create the FAISS index
    index, model = create_faiss_index(chunks)

    # Step 4: Encode the query and search in the FAISS index
    query_embedding = model.encode([query])
    query_embedding = normalize(query_embedding)

    # Search the FAISS index
    D, I = index.search(query_embedding, top_k)  # D = distances, I = indices of nearest neighbors
    # Return only the top-k similar chunks
    return [chunks[i] for i in I[0]]


# Example usage

# Example query and PDF path
# query = "Emperor Ashoka ANS SARNATH PILLAR"  # Example query to search for
# pdf_path = "../Social_Science.pdf"  # Provide the correct path to your PDF

