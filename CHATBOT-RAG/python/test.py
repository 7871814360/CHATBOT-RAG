from Rag import search_similar_chunks
user_message = "Emperor Ashoka and Sarnath Pillar"
pdf_path = "./Social_Science.pdf"
similar_chunks = search_similar_chunks(user_message, pdf_path)
print(similar_chunks)