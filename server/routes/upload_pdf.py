from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from typing import List
from asyncio import get_event_loop
from functools import partial

from modules.vector_store import load_vector_store
from modules.pdf_handlers import save_uploaded_files

from logger import logger

router = APIRouter()
ALLOWED_CONTENT_TYPES = {"application/pdf", "application/octet-stream", "application/x-pdf"}


def is_pdf_file(file: UploadFile) -> bool:
    # Accept explicit PDF content-type, generic binary uploads, or valid PDF header.
    if file.content_type in ALLOWED_CONTENT_TYPES:
        return True
    if file.filename.lower().endswith(".pdf"):
        return True

    try:
        file.file.seek(0)
        header = file.file.read(5)
        file.file.seek(0)
        return header == b"%PDF-"
    except Exception:
        return False


@router.post("/upload_pdfs", response_model=dict)
async def upload_pdfs(files:List[UploadFile] = File(...)):
    # validate all files are PDFs before doing any work
    for file in files:
        logger.info(f"Uploading file {file.filename} with content-type {file.content_type}")
        if not is_pdf_file(file):
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a PDF. Only PDF files are accepted."
            )
    try:
        logger.info(f"Received {len(files)} file(s) for upload")
        
        # save files to disk first, get back paths
        file_paths = save_uploaded_files(files)
        logger.info(f"Saved {len(file_paths)} file(s) to disk")
        
        # offload heavy sync work (embedding + upsert) to thread pool
        # so it doesn't block the async event loop
        loop = get_event_loop()
        
        await loop.run_in_executor(None, partial(load_vector_store, file_paths))
        
        logger.info("Document successfully added to vectorstore")
        return JSONResponse(
            status_code=200,
            content={"message": f"{len(file_paths)} file(s) processed and vectorstore updated"}
        )
    
    except Exception as e:
        logger.exception("Error during PDF upload")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )