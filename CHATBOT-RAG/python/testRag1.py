import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Step 1: Read the text file and separate titles and paragraphs
def read_text_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    titles = []
    paragraphs = []
    current_title = None
    current_paragraph = []

    for line in lines:
        line = line.strip()
        if line == '-----------':
            if current_title and current_paragraph:
                titles.append(current_title)
                paragraphs.append(' '.join(current_paragraph))
            current_title = None
            current_paragraph = []
        elif current_title is None:
            current_title = line
        else:
            current_paragraph.append(line)

    # Append the last title and paragraph pair if exists
    if current_title and current_paragraph:
        titles.append(current_title)
        paragraphs.append(' '.join(current_paragraph))

    return titles, paragraphs

# Step 2: Generate embeddings for the given texts (titles or paragraphs)
def generate_embeddings(texts):
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeddings = model.encode(texts, convert_to_tensor=True)
    return embeddings

# Step 3: Create a FAISS index for the paragraph embeddings
def create_faiss_index(embeddings):
    dim = embeddings.shape[1]  # Embedding dimensions
    index = faiss.IndexFlatL2(dim)  # Using L2 distance for similarity search
    index.add(embeddings)  # Add embeddings to the index
    return index

# Step 4: Search for the paragraph corresponding to the given title
def search_paragraph_by_title(title, titles, paragraphs, index, model, top_k=1):
    # Generate the embedding for the given title
    title_embedding = model.encode([title], convert_to_tensor=True)

    # Perform the search in the FAISS index
    D, I = index.search(np.array(title_embedding).astype('float32'), top_k)

    # Return the most similar paragraphs
    relevant_paragraphs = [paragraphs[i] for i in I[0]]
    return relevant_paragraphs

# Main function to process the file and perform search
def main(file_path, query_title):
    # Step 1: Read the file and separate titles and paragraphs
    titles, paragraphs = read_text_file(file_path)

    # Step 2: Generate embeddings for paragraphs
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    paragraph_embeddings = generate_embeddings(paragraphs)

    # Step 3: Create FAISS index
    faiss_index = create_faiss_index(paragraph_embeddings)

    # Step 4: Search for the paragraph corresponding to the given title
    relevant_paragraphs = search_paragraph_by_title(query_title, titles, paragraphs, faiss_index, model)
    
    return relevant_paragraphs

# Example usage
if __name__ == '__main__':
    file_path = 'output.txt'  # Specify the path to your text file
    query_title = 'Vision'  # The title you want to search for
    relevant_paragraphs = main(file_path, query_title)

    # Print the relevant paragraphs
    print(f"Relevant paragraph(s) for '{query_title}':")
    for paragraph in relevant_paragraphs:
        print(paragraph)
