# 🧑‍⚕️ Medical Assistant Chatbot - RAG System

An AI-powered medical document assistant that uses **Retrieval-Augmented Generation (RAG)** to answer medical questions based on uploaded PDF documents. This system intelligently retrieves relevant information from your medical documents and uses a large language model to provide accurate, context-aware answers.

---

## 📋 Project Overview

The **Medical Assistant Chatbot** is a full-stack application designed to help users interact with medical documents through natural language. Users can upload PDF documents containing medical information, and then ask questions about the content. The system will retrieve relevant information and provide accurate answers using advanced AI models.

### Key Features:
- 📄 **Multi-PDF Upload**: Upload multiple medical documents at once
- 💬 **Intelligent Q&A**: Ask questions and get answers based on your documents
- 🔍 **Source Tracking**: See which documents provided the answer
- 💾 **Chat History**: Maintain conversation history throughout your session
- ⚡ **Async Processing**: Non-blocking file processing for better performance
- 🔒 **Robust Error Handling**: Comprehensive validation and error management

---

## 🤖 What is RAG (Retrieval-Augmented Generation)?

RAG is a powerful AI technique that combines:

1. **Retrieval**: Searching through your documents to find relevant information
2. **Augmentation**: Enriching the language model's prompt with retrieved context
3. **Generation**: Using the LLM to generate accurate answers based on the retrieved context

### How it works in this project:
```
User Question → Vector Search (Pinecone) → Retrieve Relevant Chunks 
  → Format Context → Prompt LLM (Groq) → Answer + Source Attribution
```

**Benefits:**
- Answers grounded in your actual documents (reduces hallucinations)
- Fast retrieval using vector similarity search
- Cost-effective compared to fine-tuning large models
- Easily updatable by adding new documents

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client Layer (Streamlit)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │   Chat UI    │  │  Upload UI   │  │ History Download   │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    HTTP (REST API)
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   Backend Layer (FastAPI)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Routes                                                  │   │
│  │  ├── POST /upload_pdfs - Upload and vectorize PDFs     │   │
│  │  └── POST /ask - Query with RAG                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Core Modules                                            │   │
│  │  ├── pdf_handlers - PDF extraction & storage            │   │
│  │  ├── vector_store - Embedding & Pinecone upsertion      │   │
│  │  ├── query_handler - Retrieval logic                    │   │
│  │  └── llm - LLM chain setup (prompt + generation)        │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
    ┌──────▼─────────┐         ┌──────────▼─────┐
    │ Pinecone       │         │ External APIs   │
    │ (Vector DB)    │         ├─────────────────┤
    │                │         │ • Groq LLM      │
    │ Stores:        │         │ • Google Gemini │
    │ • Embeddings   │         │   (Embeddings)  │
    │ • Metadata     │         └─────────────────┘
    └────────────────┘
```

---

## ✨ Features

### 1. **PDF Document Management**
   - Multi-file upload support
   - PDF validation (header checking)
   - Automatic text extraction with page tracking
   - Chunking with configurable overlap (500 chars, 50 overlap)

### 2. **Vector Search**
   - Google Generative AI embeddings (768-dimensional)
   - Pinecone vector database for fast semantic search
   - Metadata preservation (source files, page numbers)
   - Serverless infrastructure on AWS

### 3. **Intelligent Q&A**
   - Context-aware answer generation
   - Source attribution with document references
   - System prompt designed for medical accuracy
   - Prevents hallucination with context grounding

### 4. **User Interface**
   - Streamlit-based web interface
   - Real-time chat with streaming responses
   - Sidebar document management
   - Session-based chat history
   - Download conversation history

### 5. **Performance**
   - Async/await for non-blocking I/O
   - Thread pool execution for heavy operations
   - Batch embedding processing
   - Efficient vectorstore upserts

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI |
| **Server** | Uvicorn |
| **Language** | Python 3.11+ |
| **LLM** | Groq (Llama 3.1 8B Instant) |
| **Embeddings** | Google Generative AI |
| **Vector DB** | Pinecone (Serverless) |
| **Processing** | LangChain + LangChain Community |
| **PDF Parsing** | PyPDF |

### Frontend
| Component | Technology |
|-----------|-----------|
| **Framework** | Streamlit |
| **Language** | Python |
| **HTTP Client** | Requests |

### Infrastructure
| Component | Service |
|-----------|---------|
| **Hosting** | Render (Backend) |
| **Vector Storage** | Pinecone (AWS Serverless) |
| **LLM Provider** | Groq |
| **Embedding Provider** | Google Cloud (Generative AI) |

### Development
| Tool | Purpose |
|------|---------|
| **Package Manager** | uv (or pip) |
| **Environment** | Python venv |
| **API Testing** | Postman |
| **Logging** | Loguru |

---

## 🔌 API Endpoints

### 1. Upload PDFs
**Endpoint:** `POST /upload_pdfs`

Upload one or multiple PDF documents to be processed and added to the vector store.

**Request:**
```bash
curl -X POST "http://localhost:8000/upload_pdfs" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

**Response (200 OK):**
```json
{
  "message": "2 file(s) processed and vectorstore updated"
}
```

**Error (400 Bad Request):**
```json
{
  "detail": "filename.pdf is not a PDF. Only PDF files are accepted."
}
```

---

### 2. Ask Question (RAG Query)
**Endpoint:** `POST /ask`

Query the uploaded documents using RAG to get context-aware answers.

**Request:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -d "question=What are the symptoms of diabetes?"
```

**Response (200 OK):**
```json
{
  "response": "Based on the provided documents, the symptoms of diabetes include...",
  "sources": [
    "medical_guide-0",
    "medical_guide-1",
    "health_handbook-3"
  ]
}
```

**Error (500 Internal Server Error):**
```json
{
  "error": "Error message details"
}
```

---

## 📁 Folder Structure

```
medical-assistant-rag/
├── main.py                          # Root entry point
├── pyproject.toml                   # Project metadata & dependencies
├── README.md                        # This file
│
├── client/                          # Streamlit Frontend
│   ├── app.py                       # Main Streamlit application
│   ├── config.py                    # Configuration (API URL)
│   ├── requirements.txt             # Frontend dependencies
│   ├── components/
│   │   ├── chat_ui.py              # Chat interface component
│   │   ├── upload_ui.py            # Document upload component
│   │   └── history_download_ui.py  # Chat history download component
│   └── utils/
│       └── api.py                  # API client functions
│
├── server/                          # FastAPI Backend
│   ├── main.py                      # FastAPI app setup & routes
│   ├── logger.py                    # Logging configuration
│   ├── requirements.txt             # Backend dependencies
│   ├── test.py                      # Unit tests
│   │
│   ├── routes/
│   │   ├── upload_pdf.py           # PDF upload endpoint
│   │   └── ask.py                  # Query endpoint
│   │
│   ├── modules/
│   │   ├── pdf_handlers.py         # PDF file operations
│   │   ├── vector_store.py         # Pinecone vectorstore management
│   │   ├── query_handler.py        # Retrieval & RAG logic
│   │   └── llm.py                  # LLM chain configuration
│   │
│   ├── middlewares/
│   │   └── exception_handler.py    # Global error handling
│   │
│   └── uploaded_docs/              # Storage for uploaded PDFs
│
├── postman/                         # Postman collections for API testing
│   ├── collections/
│   ├── environments/
│   ├── flows/
│   ├── globals/
│   │   └── workspace.globals.yaml
│   ├── mocks/
│   └── specs/
│
└── .env                            # Environment variables (not in repo)
```

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.11 or higher
- API Keys:
  - **Groq API Key** (for LLM) - [Get it here](https://console.groq.com)
  - **Google Generative AI Key** (for embeddings) - [Get it here](https://ai.google.dev)
  - **Pinecone API Key** (for vector DB) - [Get it here](https://www.pinecone.io)

### Step 1: Clone the Repository
```bash
git clone <repo-url>
cd medical-assistant-rag
```

### Step 2: Set Up Environment Variables
Copy the `.env.example` file and create your own `.env` file:
```bash
cp .env.example .env
```

Then edit the `.env` file and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
GEMINI_API_KEY=your_google_ai_key_here
PINECONE_ENV=us-east-1  # e.g., us-east-1
PINECONE_INDEX_NAME=medical-documents  # lowercase, no special characters
```

**⚠️ Important:** Never commit the `.env` file to version control. The `.env.example` file shows all required variables.

### Step 3: Install Dependencies

**Backend:**
```bash
cd server
pip install -r requirements.txt
# or using uv:
uv pip install -r requirements.txt
```

**Frontend:**
```bash
cd client
pip install -r requirements.txt
# or using uv:
uv pip install -r requirements.txt
```

### Step 4: Run the Application

**Terminal 1 - Start Backend Server:**
```bash
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

**Terminal 2 - Start Frontend (Streamlit):**
```bash
cd client
streamlit run app.py
```

The UI will open at: `http://localhost:8501`

### Step 5: Use the Application

1. **Upload Documents**: Click on the sidebar to upload PDF files
2. **Ask Questions**: Type your medical questions in the chat
3. **View Results**: Get answers with source attribution
4. **Download History**: Export your conversation

---

## 📦 Deployment

### Hosting on Render

This application is designed to be deployed on **Render** for production use.

#### Backend Deployment Steps:

1. **Create a Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Connect Your Repository**
   - Click "New +" and select "Web Service"
   - Connect your GitHub repo

3. **Configure Build Settings**
   - **Name**: `medical-assistant-backend`
   - **Environment**: `Python 3.11`
   - **Build Command**: 
     ```bash
     pip install -r server/requirements.txt
     ```
   - **Start Command** (Important):
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 10000
     ```

4. **Set Environment Variables**
   - Go to "Environment" in Render dashboard
   - Add the following variables:
     ```
     GROQ_API_KEY=your_key
     GEMINI_API_KEY=your_key
     PINECONE_API_KEY=your_key
     PINECONE_ENV=your_region
     PINECONE_INDEX_NAME=medical-documents
     ```

5. **Deploy**
   - Render will automatically deploy on every push to main branch
   - Your API will be available at: `https://your-service-name.onrender.com`

#### Frontend Deployment (Optional - Streamlit Cloud):

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and select `client/app.py`
4. Add `API_URL` as a secret pointing to your Render backend
5. Deploy

#### Important Notes:
- Render's free tier has limitations; consider paid tier for production
- Cold starts may cause initial delays
- Pinecone provides free tier with limitations; upgrade as needed
- Groq and Google AI provide free API quotas

---

## 📋 Configuration Files

### Backend Requirements (`server/requirements.txt`)
- FastAPI & Uvicorn for the web framework
- LangChain ecosystem for RAG implementation
- Pinecone for vector storage
- Google Generative AI for embeddings
- Groq LLM integration
- PyPDF for document processing
- python-dotenv for environment management

### Frontend Requirements (`client/requirements.txt`)
- Streamlit for UI
- Requests for API communication

---

## 🔧 Development

### Running Tests
```bash
cd server
python test.py
```

### Viewing API Documentation
Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Code Structure Best Practices
- **Routes**: Define API endpoints and request handling
- **Modules**: Core business logic (embeddings, retrieval, LLM)
- **Middlewares**: Global error handling and cross-cutting concerns
- **Components**: Reusable UI elements in Streamlit
- **Utils**: Helper functions and API clients

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "CORS error" | Ensure backend is running with CORS enabled |
| "API Key invalid" | Check `.env` file and verify keys are correct |
| "PDF upload fails" | Ensure file is valid PDF; check file size limits |
| "Slow responses" | May be Groq/Pinecone rate limiting; upgrade plan |
| "No answers found" | Documents may not be embedded; try re-uploading |
| "Connection refused" | Ensure both server and frontend are running |

---

## 📄 License

This project is open source. Please check the LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation at `/docs`
- Check Postman collections in the `postman/` folder

---

**Happy querying! 🚀**
