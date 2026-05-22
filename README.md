# Healthcare Assistant AI — RAG Chatbot & Voice Emergency

Hệ thống hỏi đáp y tế tự động tích hợp hai chức năng chính:

- **RAG Chatbot**: Trả lời câu hỏi sơ cấp cứu dựa trên tài liệu PDF nội bộ (FAISS + LangChain + GPT-4o-mini).
- **Emergency Voice Mode**: Kết nối giọng nói thời gian thực qua WebRTC (OpenAI Realtime API) hướng dẫn sơ cứu người ngất xỉu từng bước.

---

## Kiến trúc tổng quan

```
rag-chatbot-for-healthcare/
├── backend/
│   ├── main.py           # FastAPI server — 3 API endpoint
│   ├── services.py       # RAG chain: FAISS + LangChain + OpenAI
│   ├── build_index.py    # Script build FAISS index từ PDF
│   ├── db/
│   │   └── faiss_index/  # Vector database đã build sẵn
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Giao diện chat chính (Dark Glassmorphism)
│   │   ├── EmergencyMode.jsx # Giao diện gọi khẩn cấp (WebRTC)
│   │   ├── App.css
│   │   └── EmergencyMode.css
│   ├── package.json
│   └── vite.config.js
└── papers/               # Thư mục chứa file PDF nguồn
```

---

## Tính năng

| Tính năng | Mô tả |
|---|---|
| RAG Chatbot | Trả lời bằng tiếng Việt, chỉ dùng thông tin từ tài liệu nội bộ |
| Trích dẫn nguồn | Mỗi câu trả lời kèm link PDF có số trang để kiểm chứng |
| Emergency Voice | Nhấn "CẤP CỨU" → kết nối WebRTC giọng nói thời gian thực |
| AI sơ cứu ngất xỉu | Hướng dẫn CPR, tư thế hồi phục, gọi 115 — từng bước rõ ràng |
| Markdown rendering | Câu trả lời được render đẹp với react-markdown + GFM |
| Index có sẵn | FAISS index đã build, chạy ngay không cần embedding lại |

---

## Yêu cầu hệ thống

- **Python** 3.8+
- **Node.js** 16+ (Vite tương thích tốt nhất)
- **OpenAI API Key** — dùng cho cả Embeddings, GPT-4o-mini chat, và Realtime Voice

---

## Cài đặt & Chạy

### 1. Backend (FastAPI — cổng 8000)

```bash
cd backend

# Cài thư viện
pip install -r requirements.txt

# Tạo file môi trường
cp .env.example .env
```

Mở file `.env` và điền API Key:

```env
OPENAI_API_KEY=sk-...
```

Khởi động server:

```bash
python -m uvicorn main:app --reload
```

Server chạy tại `http://localhost:8000`.

---

### 2. Frontend (React/Vite — cổng 5173)

Mở terminal mới:

```bash
cd frontend

# Cài dependencies
npm install

# Khởi động giao diện
npm run dev
```

Mở trình duyệt tại `http://localhost:5173`.

---

## API Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/api/chat` | Gửi câu hỏi, nhận câu trả lời RAG |
| `GET` | `/health` | Kiểm tra trạng thái server |
| `GET` | `/api/voice-token` | Lấy ephemeral token cho WebRTC Realtime |
| `GET` | `/api/papers/{filename}` | Truy cập file PDF nguồn |

**Ví dụ gọi chat API:**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Cách xử lý khi người bị ngất xỉu?"}'
```

---

## Luồng hoạt động

### RAG Chatbot

```
Câu hỏi người dùng
    ↓
FAISS similarity search (top-5, threshold 0.2)
    ↓
Ghép context từ các đoạn PDF liên quan
    ↓
GPT-4o-mini sinh câu trả lời (chỉ dùng context, không hallucinate)
    ↓
Câu trả lời + trích dẫn nguồn có link PDF & số trang
```

### Emergency Voice Mode

```
Người dùng nhấn "CẤP CỨU"
    ↓
Frontend xin quyền microphone
    ↓
Gọi GET /api/voice-token → lấy ephemeral key (hết hạn sau 10 phút)
    ↓
Thiết lập WebRTC PeerConnection với OpenAI Realtime API
    ↓
AI giọng nói hướng dẫn sơ cứu ngất xỉu từng bước (gpt-realtime-2)
    ↓
Nhấn "Kết Thúc Cuộc Gọi" → đóng kết nối, giải phóng microphone
```

---

## Build lại FAISS Index (khi có tài liệu mới)

Đặt các file PDF vào thư mục `papers/`, sau đó chạy từ thư mục `backend/`:

```bash
cd backend
python build_index.py
```

Script sẽ:
1. Load tất cả PDF trong `../papers/`
2. Chia nhỏ văn bản (chunk 1200 ký tự, overlap 200)
3. Tạo embedding bằng `text-embedding-3-large`
4. Lưu FAISS index vào `./db/faiss_index/`

**Lưu ý:** Bước này tiêu tốn OpenAI API credits tùy theo kích thước tài liệu.

---

## Công nghệ sử dụng

**Backend**

| Thư viện | Mục đích |
|---|---|
| FastAPI + Uvicorn | Web server |
| LangChain | RAG orchestration |
| FAISS (faiss-cpu) | Vector store |
| OpenAI Embeddings | `text-embedding-3-large` |
| GPT-4o-mini | Sinh câu trả lời |
| OpenAI Realtime API | Voice AI khẩn cấp |
| PyPDF | Đọc file PDF |
| python-dotenv | Quản lý biến môi trường |

**Frontend**

| Thư viện | Mục đích |
|---|---|
| React 18 + Vite | UI framework |
| Axios | HTTP client |
| react-markdown + remark-gfm | Render Markdown |
| WebRTC (browser native) | Kết nối giọng nói |

---

## Lưu ý bảo mật

- File `.env` chứa API Key — **không commit lên git**.
- CORS hiện được cấu hình `allow_origins=["*"]`. Khi triển khai production, hãy giới hạn về domain cụ thể.
- Ephemeral voice token hết hạn sau **10 phút** kể từ khi tạo.

---

*Phát triển bởi NQC.*
