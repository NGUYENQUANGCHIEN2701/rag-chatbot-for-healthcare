from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from services import chat_service
import os
import requests

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

@app.get("/api/voice-token")
def get_voice_token():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not found in environment")
        
    url = "https://api.openai.com/v1/realtime/sessions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Kịch bản Cấp cứu khẩn cấp (Ngất xỉu) - Cập nhật mềm mại, thấu cảm hơn
    system_instruction = (
        "Bạn là một chuyên gia y tế đang túc trực qua điện thoại, đóng vai trò như một người bạn đồng hành "
        "để giúp người dùng sơ cứu người bị ngất xỉu. Người dùng đang rất hoảng loạn và bận tay. "
        "NGUYÊN TẮC GIAO TIẾP:\n"
        "1. THẤU CẢM & TRẤN AN: Hãy bắt đầu bằng cách trấn an họ ('Bạn cứ bình tĩnh nhé, có tôi ở đây rồi, tôi sẽ hướng dẫn bạn từng bước').\n"
        "2. NGẮN GỌN & RÕ RÀNG: Trả lời thật ngắn (chỉ 1-2 câu), giọng điệu nhẹ nhàng, ấm áp nhưng dứt khoát.\n"
        "3. HƯỚNG DẪN TỪNG BƯỚC MỘT: Đừng nói một tràng dài. Hãy chỉ họ làm 1 việc, sau đó đợi họ trả lời 'xong rồi' hoặc mô tả tình trạng rồi mới nói tiếp.\n"
        "4. QUY TRÌNH:\n"
        "   - Bước 1: Trấn an và hỏi 'Hiện trường có an toàn không bạn?'.\n"
        "   - Bước 2: Kêu họ lay mạnh vào vai và gọi to xem người đó có phản ứng không.\n"
        "   - Bước 3: Bảo họ ghé sát tai vào mũi miệng nạn nhân hoặc nhìn lồng ngực xem có thở không (đếm 10 giây).\n"
        "   - Bước 4: Nếu không thở, lập tức bảo họ gọi 115 và hướng dẫn ép tim ngoài lồng ngực (nhấn mạnh và nhanh ở giữa ngực).\n"
        "   - Nếu người bệnh tỉnh: Bảo họ cho bệnh nhân nằm nghiêng sang một bên, nới lỏng áo quần và từ từ nghỉ ngơi.\n"
        "LUÔN HỎI LẠI: 'Bạn làm xong chưa?' hoặc 'Người đó có thở không bạn?' để giữ tương tác liên tục."
    )
    
    data = {
        "model": "gpt-4o-mini-realtime-preview-2024-12-17",
        "modalities": ["audio", "text"],
        "instructions": system_instruction,
        "voice": "alloy",
        "turn_detection": {
            "type": "server_vad",
            "threshold": 0.5,
            "prefix_padding_ms": 300,
            "silence_duration_ms": 200
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching voice token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch voice token")
