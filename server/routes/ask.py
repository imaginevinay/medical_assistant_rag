from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from asyncio import get_event_loop
from functools import partial
from modules.query_handler import get_retriever, query_chain
from modules.llm import get_llm_chain
from logger import logger

router = APIRouter()

def run_query(question: str) -> dict:
    retriever = get_retriever(question)
    chain = get_llm_chain(retriever)
    return query_chain(chain, question)

@router.post("/ask")
async def ask(question: str = Form(...)):
    try:
        logger.info(f"User query: {question}")
        loop = get_event_loop()
        result = await loop.run_in_executor(None, partial(run_query, question))
        logger.info("Query successful")
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        logger.exception("Error processing question")
        return JSONResponse(status_code=500, content={"error": str(e)})