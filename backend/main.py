from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from services import chat_service
import os

app = FastAPI(title="RAG Chatbot API")

# Mount the papers directory so frontend can access PDFs
papers_dir = os.path.join(os.path.dirname(__file__), "..", "papers")
if os.path.exists(papers_dir):
    app.mount("/api/papers", StaticFiles(directory=papers_dir), name="papers")


# Setup CORS to allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    answer = chat_service.get_answer(request.message)
    return ChatResponse(answer=answer)

@app.get("/health")
def health_check():
    return {"status": "ok"}
