import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


# Step 1: Load JSON Data
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


# Step 2: Extract Paragraphs and Subsection Titles from JSON Data
def extract_paragraphs_and_titles(data):
    paragraphs_with_titles = []
    
    # Iterate over sections and subsections
    for section in data.get("sections", []):
        # Add main section paragraphs and title
        for paragraph in section.get("paragraphs", []):
            paragraphs_with_titles.append({
                "paragraph": paragraph,
                "section_title": section["section_title"],
                "subsection_title": " "  # No subsection title for main section
            })
        
        # Add subsection paragraphs and their titles
        if "subsections" in section:
            for subsection in section["subsections"]:
                for paragraph in subsection.get("paragraphs", []):
                    paragraphs_with_titles.append({
                        "paragraph": paragraph,
                        "section_title": section["section_title"],
                        "subsection_title": subsection["subsection_title"]
                    })
    
    return paragraphs_with_titles


# Step 3: Initialize Sentence-Transformer Model and Generate Embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(paragraphs):
    embeddings = model.encode(paragraphs, convert_to_tensor=True)
    return embeddings


# Step 4: Build Faiss Index for Efficient Search
def build_faiss_index(embeddings):
    embeddings = np.array(embeddings)
    dim = embeddings.shape[1]  # Dimensionality of the embeddings
    index = faiss.IndexFlatL2(dim)  # L2 distance metric for similarity
    index.add(embeddings)  # Add embeddings to the Faiss index
    return index


# Step 5: Query the Faiss Index and Retrieve Relevant Paragraphs

def search_faiss_index(query, index, paragraphs, top_k=3, similarity_threshold=0.6):
    # Generate the embedding for the query
    query_embedding = model.encode([query], convert_to_tensor=True)
    query_embedding = np.array(query_embedding)  # Convert to numpy array
    
    # Search the Faiss index for the most similar paragraphs
    D, I = index.search(query_embedding, top_k)  # D is distances, I is indices
    
    # Fetch the top_k most similar paragraphs
    similar_paragraphs = [paragraphs[i] for i in I[0]]
    
    # Filter out paragraphs with similarity below the threshold (0.6)
    filtered_paragraphs = []
    filtered_distances = []
    
    for p, d in zip(similar_paragraphs, D[0]):
        if d < similarity_threshold:
            filtered_paragraphs.append(p)
            filtered_distances.append(d)
    
    return filtered_paragraphs, filtered_distances

# Step 6: Main Function to Load Data, Build Index, and Perform Search
def get_paragraphs(query):
    # Load data and extract paragraphs with titles
    data = load_json('./Policy.json')  # Replace with the path to your JSON file
    paragraphs_with_titles = extract_paragraphs_and_titles(data)
    
    # Add section context to the embeddings for better differentiation
    paragraphs_with_context = [
        f"{item['section_title']} - {item['paragraph']}" for item in paragraphs_with_titles
    ]
    
    # Generate embeddings for the paragraphs with section context
    embeddings = generate_embeddings(paragraphs_with_context)
    
    # Build the Faiss index
    index = build_faiss_index(embeddings)
    
    # Generate the embedding for the enhanced query
    query_embedding = model.encode([query], convert_to_tensor=True)
    query_embedding = np.array(query_embedding)  # Convert to numpy array
    
    # Search the Faiss index for the most similar paragraphs
    D, I = index.search(query_embedding, 3)  # Return top 3 results
    
    # Initialize the response string
    response = ""
    
    # Construct the response with paragraph, similarity score, and section titles
    for i, distance in enumerate(D[0][:2]):
        if distance:
            # Use the index from Faiss search result to get the corresponding paragraph and titles
            paragraph_idx = I[0][i]
            # Get the corresponding paragraph with its section and subsection titles
            paragraph_info = paragraphs_with_titles[paragraph_idx]
            section_title = paragraph_info["section_title"]
            subsection_title = paragraph_info["subsection_title"]
            # Append the section title, subsection title, paragraph, and similarity score
            response += f"**{i + 1}. {section_title}**"
            if subsection_title:
                response += f"** - {subsection_title}**"
            response += f"\n{paragraph_info['paragraph']} (Similarity: {distance:.2f})\n\n"
            # response += f"\n{paragraph_info['paragraph']}\n\n"
    
    return response

# if __name__ == '__main__':
#     query = "Preamble" 
#     print(get_paragraphs(query)) 