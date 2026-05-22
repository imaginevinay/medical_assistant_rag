from logger import logger
from typing import List
from pydantic import PrivateAttr
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone
from modules.llm import get_llm_chain
import os

# module level — initialized once at startup
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(os.environ["PINECONE_INDEX_NAME"])
embed_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

class SimpleRetriever(BaseRetriever):
    _docs:List[Document] = PrivateAttr()

    def __init__(self, documents: List[Document]):
        super().__init__()
        self._docs = documents

    def _get_relevant_documents(self, query: str) -> List[Document]:
        return self._docs


def get_retriever(question:str) -> SimpleRetriever:
    """Embeds question, fetches top-k from Pinecone, returns a retriever."""
    embedded_query = embed_model.embed_query(question)
    res = index.query(vector=embedded_query, top_k=3, include_metadata=True)
    docs = [
        Document(
            page_content=match["metadata"].get("text", ""),
            metadata=match["metadata"]
        )
        for match in res["matches"]
    ]
    return SimpleRetriever(docs)


def query_chain(chain, user_input:str) -> dict:
    """Invokes the chain and shapes the response."""
    try:
        logger.debug(f"Running chain for input {user_input}")
        result = chain.invoke(user_input)
        response = {
            "response" : result["answer"],
            "sources": [doc.metadata.get("source", "") for doc in result["source_documents"]]
        }
        logger.debug(f"Chain response: {response}")
        return response
    except Exception as e:
        logger.exception("Error on query chain")
        return {"response": "Something went wrong. Please try again.", "sources": []}