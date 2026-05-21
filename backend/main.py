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
        
    url = "https://api.openai.com/v1/realtime/client_secrets"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Kịch bản Cấp cứu khẩn cấp (Ngất xỉu) - Hướng dẫn chuẩn, từng bước
    system_instruction = (
        "Bạn là chuyên gia y tế hướng dẫn sơ cứu người ngất xỉu qua điện thoại. "
        "Người dùng đang hoảng loạn và bận tay. "
        "NGUYÊN TẮC GIAO TIẾP:\n"
        "1. TRẤN AN: Bắt đầu bằng câu trấn an ngắn gọn.\n"
        "2. RÕ RÀNG: Mỗi lần chỉ hướng dẫn 1 việc.\n"
        "3. KIỂM TRA: Luôn hỏi lại để xác nhận đã làm xong.\n"
        "QUY TRÌNH CHUẨN (CHỈ TỪNG BƯỚC):\n"
        "- Bước 1: Hỏi hiện trường có an toàn không.\n"
        "- Bước 2: Kiểm tra đáp ứng: lay vai, gọi to xem có phản ứng không.\n"
        "- Bước 3: Kiểm tra thở 10 giây: nhìn lồng ngực, nghe hơi thở, cảm nhận luồng khí.\n"
        "- Bước 4: Nếu KHÔNG thở hoặc thở bất thường: gọi 115 ngay và bắt đầu ép tim ngoài lồng ngực.\n"
        "- Bước 5: Nếu CÓ thở: đặt nạn nhân ở tư thế hồi phục, nới lỏng quần áo, theo dõi liên tục.\n"
        "- Bước 6: Nếu nạn nhân tỉnh: trấn an, cho ngồi dậy từ từ, theo dõi dấu hiệu tái ngất và gọi cấp cứu nếu cần.\n"
        "LUÔN HỎI LẠI: 'Bạn làm xong chưa?' hoặc 'Người đó có thở không?'"
    )
    
    data = {
        "expires_after": {
            "anchor": "created_at",
            "seconds": 600
        },
        "session": {
            "type": "realtime",
            "model": "gpt-realtime-2",
            "instructions": system_instruction,
            "audio": {
                "input": {
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200
                    }
                }
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if not response.ok:
            error_detail = response.text.strip()
            print(f"Error fetching voice token: {response.status_code} {error_detail}")
            raise HTTPException(
                status_code=500,
                detail=f"Voice token error: {response.status_code} {error_detail}"
            )
        return response.json()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching voice token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch voice token")
