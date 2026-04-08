import os
import pinecone 
from langchain.vectorstores.pinecone import Pinecone
from app.chat.embeddings.openai import OpenAIEmbeddings

pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV_NAME"))    

vector_store = Pinecone.from_existing_index(os.getenv("PINECONE_INDEX_NAME"), OpenAIEmbeddings())

def build_retriever(chat_args,k):
    search_kwargs={
        "k": k,
        "filter":{"pdf_id":chat_args.pdf_id}
        }
    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
    return retriever    