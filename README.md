# 🤖 RagChatbot - Hệ thống Hỏi đáp Thông minh với Tài liệu PDF

Chào mừng bạn đến với **RagChatbot**, một giải pháp hỏi đáp tự động sử dụng kỹ thuật **Retrieval-Augmented Generation (RAG)**. Hệ thống cho phép bạn "trò chuyện" trực tiếp với các tệp dữ liệu PDF (như tài liệu y tế, hướng dẫn sơ cứu, báo cáo khoa học...) một cách chính xác và hiệu quả.

---

## ✨ Tính năng nổi bật

- **🔍 Tìm kiếm thông minh**: Sử dụng Vector Database (FAISS) để tìm kiếm ngữ nghĩa chính xác thay vì chỉ khớp từ khóa đơn thuần.
- **🧠 Phản hồi tự nhiên**: Tích hợp mô hình ngôn ngữ lớn (LLM) của OpenAI để tổng hợp câu trả lời mạch lạc, dễ hiểu.
- **📍 Trích dẫn nguồn**: Cung cấp số trang và tên file tài liệu gốc cho mỗi câu trả lời để đảm bảo tính minh bạch.
- **⚡ Tốc độ vượt trội**: Xử lý hàng trăm trang tài liệu trong tích tắc nhờ chỉ mục vector hiệu năng cao.

---

## 📸 Demo Output

Dưới đây là ví dụ chatbot trả lời các câu hỏi về **Sơ cấp cứu** dựa trên tài liệu trong thư mục `papers/`:

> **Người dùng:** *Khi nào nên đi cấp cứu?*  
> **Chatbot:** Nên đi cấp cứu ngay khi có các tình huống sau:
> - Mất ý thức, hôn mê. (source: page 89)
> - Chân thương sọ não, gãy xương do ngã cao. (source: page 89)
> - Bỏng sâu. (source: page 89)
> ...
> - **Gọi 115** để được tư vấn và vận chuyển nạn nhân đến bệnh viện gần nhất. (source: page 9)

> **Người dùng:** *Khi bị ngất xỉu, sơ cấp cứu như thế nào?*  
> **Chatbot:**
> 1. Đặt nạn nhân nằm xuống, nâng chân lên để tăng máu về não.
> 2. Đảm bảo thông thoáng khí.
> 3. Kiểm tra mạch và nhịp thở; nếu cần tiến hành hô hấp nhân tạo.
> ... (Nguồn: papers/so_cap_cuu_3.pdf:5)

---

## 📑 Cấu trúc dự án

```text
RagChatbot/
├── papers/               # 📚 Nơi chứa các file PDF đầu vào (Data source)
├── db/                   # 🗄️ Lưu trữ cơ sở dữ liệu vector (FAISS Index)
├── build_index.py        # 🛠️ Script xử lý PDF & xây dựng chỉ mục
├── chat.py               # 💬 Giao diện Chatbot chính
├── requirements.txt      # 📦 Danh sách thư viện cần thiết
└── .env                  # 🔑 Cấu hình OpenAI API Key
```

---

## 🚀 Hướng dẫn cài đặt & Sử dụng

### 1. Cài đặt môi trường

Yêu cầu **Python 3.8+**. Khuyến khích sử dụng môi trường ảo:

```bash
# Tạo và kích hoạt môi trường ảo
python3 -m venv venv
source venv/bin/activate  # Linux/macOS

# Cài đặt thư viện
pip install -r requirements.txt
```

### 2. Cấu hình API Key

Tạo file `.env` tại thư mục gốc:
```text
OPENAI_API_KEY=sk-xxxx... # Thay bằng key của bạn
```

### 3. Quy trình vận hành

1.  **Chuẩn bị dữ liệu**: Chép các file PDF vào thư mục `papers/`.
2.  **Xây dựng chỉ mục**: Chạy lệnh để "dạy" chatbot nội dung tài liệu:
    ```bash
    python3 build_index.py
    ```
3.  **Bắt đầu hỏi đáp**:
    ```bash
    python3 chat.py
    ```

---

## 🛠 Công nghệ sử dụng

- **LangChain**: Khung xương kết nối LLM và dữ liệu.
- **OpenAI (GPT-5/Embeddings)**: Bộ não xử lý ngôn ngữ.
- **FAISS**: Thư viện tìm kiếm vector cực nhanh từ Facebook AI.
- **PyPDF**: Trình đọc nội dung tài liệu PDF.

---
*Phát triển bởi NQC.*
