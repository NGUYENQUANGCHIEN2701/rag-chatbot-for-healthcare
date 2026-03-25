# RagChatbot - Hệ thống Hỏi đáp với Tài liệu PDF (RAG)

Dự án này triển khai một chatbot sử dụng kỹ thuật **Retrieval-Augmented Generation (RAG)** để trả lời các câu hỏi dựa trên nội dung các file PDF có sẵn trong thư mục `papers/`.

## 📑 Cấu trúc dự án

```text
RagChatbot/
├── papers/               # Thư mục chứa các file PDF đầu vào
├── db/                   # Thư mục lưu trữ cơ sở dữ liệu vector (FAISS)
│   └── faiss_index/      # Chỉ mục FAISS đã được xây dựng
├── build_index.py        # Script để đọc PDF và xây dựng chỉ mục vector
├── chat.py               # Script giao diện chat/truy vấn chính
├── chatbot.py            # Logic xử lý chatbot (nếu có tách riêng)
├── requirements.txt      # Danh sách các thư viện cần thiết
└── .env                  # File cấu hình biến môi trường (API Key)
```

## 🚀 Hướng dẫn sử dụng

### 1. Cài đặt môi trường

Yêu cầu Python 3.8 trở lên. Nên sử dụng môi trường ảo (venv).

```bash
# Tạo môi trường ảo
python3 -m venv venv

# Kích hoạt môi trường ảo (Linux/macOS)
source venv/bin/activate

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### 2. Cấu hình API Key

Tạo một file `.env` ở thư mục gốc và thêm mã OpenAI API Key của bạn:

```text
OPENAI_API_KEY=your_api_key_here
```

### 3. Chuẩn bị dữ liệu

Copy các file tài liệu PDF mà bạn muốn chatbot học vào thư mục `papers/`.

### 4. Xây dựng chỉ mục (Index)

Chạy script sau để xử lý tài liệu và lưu vào cơ sở dữ liệu vector:

```bash
python3 build_index.py
```

### 5. Bắt đầu Chat

Sau khi đã xây dựng xong chỉ mục, bạn có thể bắt đầu hỏi đáp với tài liệu:

```bash
python3 chat.py
```

## 🛠 Công nghệ sử dụng

- **LangChain**: Framework để xây dựng ứng dụng LLM.
- **OpenAI (GPT & Embeddings)**: Mô hình ngôn ngữ và chuyển đổi văn bản thành vector.
- **FAISS**: Thư viện tìm kiếm vector hiệu năng cao.
- **PyPDF**: Thư viện đọc nội dung file PDF.
