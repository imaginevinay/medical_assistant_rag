import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.documents import Document

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

def get_llm_chain(retriever):
    # initialize GROQ LLM 
    llm=ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.1-8b-instant"
    )
    # define chat prompt template with context and question placeholders
    prompt=ChatPromptTemplate.from_template(
        """
        You are **MediBot**, an AI-powered assistant trained to help users understand \
        medical documents and health-related questions.
        Your job is to provide clear, accurate, and helpful responses based **only on the provided context**.

        ---
        🔍 **Context**:
        {context}

        🙋 **User Question**:
        {question}

        ---
        💬 **Answer**:
        - Respond in a calm, factual, and respectful tone.
        - Use simple explanations when needed.
        - If the context does not contain the answer, say: \
        "I'm sorry, but I couldn't find relevant information in the provided documents."
        - Do NOT make up facts.
        - Do NOT give medical advice or diagnoses.
        """        
    )
    # run retriever and passthorugh on same input (user question)
    rag_chain = RunnableParallel(
        {
            # fetch relevant docs from vector store, then join them into a single string for prompt
            "context": retriever | format_docs,
            # pass raw question string 
            "question": RunnablePassthrough(),
            # keep raw document object so the caller can inspect source metadata
            "source_documents": retriever
        }
    #pipe the merged dict into prompt -> llm -> string parser and store result as answer
    ).assign(answer=prompt | llm | StrOutputParser())
    # return this chain, caller simply uses rag_chain.invoke("question")
    return rag_chain