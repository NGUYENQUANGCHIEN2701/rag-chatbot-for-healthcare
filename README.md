# 🤖 Healthcare Assistant AI - RAG Chatbot

Chào mừng bạn đến với **Healthcare Assistant AI**, một giải pháp hỏi đáp tự động sử dụng kỹ thuật **Retrieval-Augmented Generation (RAG)** với kiến trúc hiện đại (FastAPI + React). Hệ thống cho phép bạn "trò chuyện" trực tiếp với các tài liệu y tế (đã được lập chỉ mục) thông qua giao diện web trực quan, đẹp mắt.

---

## ✨ Tính năng nổi bật

- **🔍 Kiến trúc RAG Chuẩn**: Sử dụng Vector Database (FAISS) kết hợp LangChain.
- **🧠 Backend FastAPI**: Hiệu năng cao, dễ dàng mở rộng. Tích hợp OpenAI GPT-5o-mini tối ưu.
- **💻 Frontend React**: Giao diện UI Chatbot đẹp mắt, Dark Mode Glassmorphism hiện đại, dễ sử dụng.
- **⚡ Đã có sẵn Dữ liệu**: Dữ liệu đã được index vào `backend/db/faiss_index` nên không cần tốn thời gian embedding lại!

---

## 📑 Cấu trúc dự án mới

```text
rag-chatbot-for-healthcare/
├── backend/                  # ⚙️ Thư mục chứa mã nguồn Backend (Python/FastAPI)
│   ├── db/                   # 🗄️ Chứa Vector Database (FAISS index) đã tạo sẵn
│   ├── main.py               # 🚀 File chạy chính của server FastAPI
│   ├── services.py           # 🧠 Logic AI LangChain, kết nối OpenAI
│   ├── build_index.py        # 🛠️ Script tạo index (chỉ dùng khi có data mới)
│   ├── requirements.txt      # 📦 Thư viện Python
│   └── .env.example          # 🔑 Mẫu cấu hình biến môi trường
├── frontend/                 # 🌐 Thư mục chứa mã nguồn Frontend (ReactJS/Vite)
│   ├── src/                  # 🎨 Mã nguồn React components & CSS
│   ├── package.json          # 📦 Cấu hình Node & Dependencies
│   └── vite.config.js
└── papers/                   # 📚 Nơi lưu các file PDF gốc
```

---

## 🚀 Hướng dẫn cài đặt & Sử dụng

### 1. Cài đặt Backend (API Server)

Yêu cầu **Python 3.8+**. Mở terminal và chạy các lệnh sau:

```bash
cd backend

# Cài đặt thư viện
pip install -r requirements.txt

# Tạo file cấu hình và điền API Key
cp .env.example .env
# Mở file .env và nhập OPENAI_API_KEY=sk-... của bạn

# Chạy server FastAPI (chạy trên cổng 8000)
python -m uvicorn main:app --reload
```

### 2. Cài đặt Frontend (Giao diện Web)

Yêu cầu **Node.js**. Đã được khởi tạo bằng Vite tương thích cực tốt với môi trường Node 16.x. Mở một terminal mới và chạy:

```bash
cd frontend

# Cài đặt dependencies (React, Axios,...)
npm install

# Khởi chạy giao diện web
npm run dev
```

### 3. Trải nghiệm
Mở trình duyệt theo đường dẫn hiển thị ở terminal `frontend` (thường là `http://localhost:5173`). Bạn có thể bắt đầu chat ngay với trợ lý AI!

---

## 🛠 Công nghệ sử dụng

- **Backend**: FastAPI, LangChain, OpenAI, FAISS, PyPDF.
- **Frontend**: React 18, Vite, Axios, CSS Vanilla (Glassmorphism UI).

---
*Phát triển bởi NQC. Refactored architecture.*
