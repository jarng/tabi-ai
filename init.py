from dotenv import load_dotenv
import os
import uuid

from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

load_dotenv()

# Load document
print("Initializing database...")
loader = CSVLoader(file_path="./data.csv")
data = loader.load()

# embed models (openai)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
embeddings_model = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model="text-embedding-3-small",
    dimensions=512,
)

# split text to chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(data)

for doc in documents:
    id = ""
    city = ""
    content = doc.page_content.split("\n")
    for item in content:
        entry = item.split(":")
        key = entry[0]
        if key == "id":
            id = entry[1].strip()
        if key == "city":
            city = entry[1].strip()

    doc.metadata = {"id": id, "city": city}

# # init db and collection
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")
print("Initializing collection...")
docsearch = PineconeVectorStore.from_documents(
    documents=documents, embedding=embeddings_model, index_name=PINECONE_INDEX_NAME
)
print("Finished!")
