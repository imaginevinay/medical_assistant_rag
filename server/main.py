from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handler import catch_exception_middleware
from routes.upload_pdf import router as upload_router
from routes.ask import router as ask_router

app = FastAPI(title="Medical Assistant API", description="API for AI Medical Assistant Chatbot")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# middleware exception handlers
app.middleware("http")(catch_exception_middleware)
# routers

# 1. /upload : upload PDF docs
app.include_router(upload_router)
# 2. /query : ask query on the docs
app.include_router(ask_router)
