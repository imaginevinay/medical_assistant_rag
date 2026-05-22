import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec

# document stuff
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
UPLOAD_DIR = "./uploaded_docs"
# ensure UPLOAD_DIR is created if not manually
os.makedirs(UPLOAD_DIR, exist_ok=True)

# initialize pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# define serverless index spec
spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)

# fetch names of existing indexes to avoid duplicate creation
existing_indexes = [i["name"] for i in pc.list_indexes()]

# if index not exist create new one
if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=3072,
        metric="cosine",
        spec=spec
    )
    # index creation takes time poll until created
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)

# index created ovber here grab it 
index = pc.Index(PINECONE_INDEX_NAME)

def load_vector_store(file_paths: list[str]) -> None:
    """
    Accepts a list of file paths, chunks, embeds and upserts to Pinecone.
    """
    # initialize the embedding model
    embed_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
    # start processing
    for file_path in file_paths:
        # load PDF pages as langchain doc objects
        loader = PyPDFLoader(file_path)
        document = loader.load()
        
        # split in chunks for embedding
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(document)
        
        # extract raw text and metadata seperately for pinecone upsert
        text = [chunk.page_content for chunk in chunks] 
        metadata = [{**chunk.metadata, "text": chunk.page_content} for chunk in chunks]
        # geenrate unique id per chunk -> filename stem + chunk index
        ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]
        print(f"🔍 Embedding {len(text)} chunks from {Path(file_path).name}...")
        
        # embed all chunks in 1 batched call
        embeddings = embed_model.embed_documents(text)
        print("📤 Uploading to Pinecone...")
        
        vectors = [
            {"id": _id, "values": embedding, "metadata" : metadata}
            for _id, embedding, metadata in zip(ids, embeddings, metadata)
        ]
        
        # upsert in batch of 100 to stay within recommended pinecone payload size
        batch_size = 100
        with tqdm(total=len(vectors), desc=f"Upserting {Path(file_path).name}") as progress:
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i : i + batch_size]
                index.upsert(vectors=batch)
                progress.update(len(batch))
        
        print(f"✅ Upload complete for {file_path}")