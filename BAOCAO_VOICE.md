# BÁO CÁO: TÍCH HỢP TÍNH NĂNG "AI VOICE KHẨN CẤP" (REALTIME WEBRTC)

## 1. MỤC TIÊU VÀ BỐI CẢNH
Hệ thống RAG Chatbot Y tế được bổ sung thêm một tính năng chuyên biệt dành riêng cho trường hợp khẩn cấp: **Sơ cấp cứu bệnh nhân ngất xỉu**.
Trong tình huống này, người dùng thường rơi vào trạng thái hoảng loạn, hai tay bận rộn để thao tác trên cơ thể người bệnh. Do đó, phương thức chat bằng văn bản truyền thống (Text-based UI) không còn hiệu quả.
=> Giải pháp: Tích hợp chức năng Voice AI tương tác thời gian thực (Full-duplex Realtime) như một người đồng hành trực tuyến, tự động lắng nghe và phát lại giọng nói mà không cần người dùng thao tác thiết bị.

## 2. KIẾN TRÚC HỆ THỐNG
Hệ thống sử dụng kiến trúc **Client-Server-LLM** kết hợp giao thức **WebRTC** để giảm thiểu độ trễ (latency < 500ms).

*   **Frontend (React/Vite)**: Chịu trách nhiệm mở Microphone, hiển thị giao diện khẩn cấp trực quan và tạo kết nối WebRTC (Peer-to-Peer) thẳng đến máy chủ OpenAI. Âm thanh từ AI được phát qua một `<audio>` element với `autoplay = true`.
*   **Backend (FastAPI)**: Đóng vai trò là "Cổng bảo mật" (Security Gate). Thay vì làm Proxy chuyển tiếp âm thanh (gây tăng độ trễ), Backend chịu trách nhiệm tạo và quản lý Session Token tạm thời (Client Secret) từ OpenAI thông qua endpoint `POST /v1/realtime/client_secrets`, đồng thời nạp (inject) Kịch bản Prompt khẩn cấp và cấu hình VAD.
*   **LLM (OpenAI Realtime API - `gpt-realtime-2`)**: Xử lý luồng âm thanh trực tiếp từ người dùng, nhận diện giọng nói (STT), suy luận theo Prompt (LLM), và tổng hợp giọng nói (TTS) trả về cùng lúc.
*   **RAG Engine (Chat thông thường)**: Sử dụng LangChain + FAISS vector store với embedding model `text-embedding-3-large` và LLM `gpt-4o-mini` để trả lời các câu hỏi sơ cấp cứu từ kho tài liệu nội bộ.

## 3. LUỒNG HOẠT ĐỘNG (FLOW)

Dưới đây là luồng hoạt động từng bước từ khi người dùng bấm nút "CẤP CỨU":

1. **Khởi tạo (Initialization):**
   * Người dùng bấm nút **🚨 CẤP CỨU** trên Frontend.
   * Giao diện `EmergencyMode` (Overlay) hiển thị toàn màn hình, chặn mọi thao tác chat văn bản thông thường.
   * Component tự động gọi `startEmergencyCall()` thông qua `useEffect`.

2. **Xin cấp quyền Microphone:**
   * Frontend gọi `navigator.mediaDevices.getUserMedia({ audio: true })` để xin quyền Microphone.

3. **Lấy Client Secret Token:**
   * Frontend gọi `GET /api/voice-token` trên Backend.
   * Backend dùng thư viện `requests` gọi lên OpenAI API endpoint `POST /v1/realtime/client_secrets` với API Key gốc.
   * Backend truyền kèm payload gồm:
     - `expires_after`: Token hết hạn sau **600 giây (10 phút)** tính từ thời điểm tạo (`anchor: "created_at"`).
     - `session.model`: `"gpt-realtime-2"`
     - `session.instructions`: System Instruction khẩn cấp 6 bước (xem Mục 4).
     - `session.audio.input.turn_detection`: Cấu hình Server VAD với `threshold: 0.5`, `prefix_padding_ms: 300`, `silence_duration_ms: 200`.
   * OpenAI trả về JSON chứa `client_secret`. Backend gửi toàn bộ JSON này về cho Frontend.
   * Frontend trích xuất token tại trường `sessionData.value`.

4. **Kết nối WebRTC (Connection Setup):**
   * Frontend tạo đối tượng `RTCPeerConnection`.
   * Frontend lấy audio track từ stream Microphone và gắn vào PeerConnection bằng `pc.addTrack(stream.getTracks()[0])`.
   * Frontend lắng nghe sự kiện `pc.ontrack` để nhận audio stream từ AI và gán vào `<audio>` element để phát ra loa.
   * Frontend tạo Data Channel `"oai-events"` để nhận các sự kiện realtime từ OpenAI (transcript, trạng thái phiên,...).
   * Frontend tạo SDP Offer (`pc.createOffer()`), set local description, sau đó gửi SDP trực tiếp lên `https://api.openai.com/v1/realtime/calls` bằng HTTP POST với header `Authorization: Bearer <ephemeralKey>` và `Content-Type: application/sdp`.
   * OpenAI phản hồi SDP Answer dạng text. Frontend set remote description để hoàn tất bắt tay WebRTC.

5. **Tương tác Thời gian thực (Full-duplex Interaction):**
   * Người dùng nói -> Luồng âm thanh được đẩy thẳng đến OpenAI qua WebRTC.
   * Nhờ công nghệ **Server VAD (Voice Activity Detection)**, OpenAI tự động nhận biết lúc nào người dùng ngừng nói để bắt đầu xử lý (silence sau 200ms).
   * Nếu AI đang nói (hướng dẫn ép tim) mà người dùng hốt hoảng la lên *"Anh ấy tỉnh rồi!"*, tính năng Interruption (ngắt lời) của Realtime API sẽ ngay lập tức cắt ngang âm thanh của AI và xử lý câu nói mới của người dùng.

6. **Kết thúc (Termination):**
   * Người dùng nhấn "Kết thúc cuộc gọi" hoặc component bị unmount.
   * Frontend giải phóng Microphone (`streamRef.current.getTracks().forEach(track => track.stop())`) và đóng PeerConnection (`pcRef.current.close()`).
   * State `isEmergencyMode` được reset về `false`, trả người dùng về giao diện chat thông thường.

## 4. TỐI ƯU HÓA TRẢI NGHIỆM (UX/UI & PROMPT)

*   **UI - Xóa bỏ rào cản**: Giao diện cấp cứu hiển thị Overlay che toàn bộ website để tập trung tuyệt đối. Có vòng tròn hiệu ứng sóng âm đập theo nhịp (Pulsing Animation với class CSS `active`) để tạo cảm giác "AI vẫn đang lắng nghe" nhưng không chiếm sự chú ý. Icon microphone SVG được tích hợp trực tiếp (không phụ thuộc thư viện icon ngoài).

*   **Prompt Engineering - Kịch bản 6 bước chuẩn y tế**: System Instruction được thiết kế theo quy trình sơ cứu chuẩn, bao gồm:
    1. **Trấn an** bằng câu ngắn gọn ngay đầu phiên.
    2. **Rõ ràng**: Mỗi lần chỉ hướng dẫn 1 việc.
    3. **Kiểm tra**: Luôn hỏi lại xác nhận đã làm xong.
    4. **6 bước quy trình CPR**:
       - Bước 1: Kiểm tra hiện trường an toàn.
       - Bước 2: Kiểm tra đáp ứng (lay vai, gọi to).
       - Bước 3: Kiểm tra thở 10 giây (nhìn-nghe-cảm nhận).
       - Bước 4: Không thở / thở bất thường → gọi 115 + bắt đầu ép tim.
       - Bước 5: Có thở → tư thế hồi phục, nới lỏng quần áo, theo dõi.
       - Bước 6: Nạn nhân tỉnh → trấn an, ngồi dậy từ từ, gọi cấp cứu nếu cần.
    5. **Xác nhận liên tục**: Luôn kết thúc bằng "Bạn làm xong chưa?" hoặc "Người đó có thở không?".

*   **Xử lý lỗi**: Nếu kết nối thất bại ở bất kỳ bước nào, frontend hiển thị thông báo `"Lỗi kết nối! Vui lòng gọi 115 ngay lập tức."` để đảm bảo người dùng luôn có phương án dự phòng.

## 5. CÁC ENDPOINT API

| Endpoint | Method | Mô tả |
|---|---|---|
| `/api/chat` | POST | Chat RAG thông thường (FAISS + gpt-4o-mini) |
| `/api/voice-token` | GET | Tạo Client Secret Token cho WebRTC |
| `/api/papers/{filename}` | GET | Phục vụ file PDF tài liệu tham khảo |
| `/health` | GET | Health check Backend |

## 6. TỔNG KẾT
Việc chuyển đổi sang kiến trúc WebRTC trực tiếp thông qua Client Secret Token mang lại 2 lợi ích cốt lõi:
1. **Độ trễ siêu thấp**: Backend không tham gia vào đường truyền audio. Toàn bộ luồng âm thanh đi thẳng Client ↔ OpenAI. Cực kỳ quan trọng trong sơ cấp cứu "thời gian là vàng".
2. **Tiết kiệm tài nguyên máy chủ**: Backend không phải duy trì các luồng WebSocket liên tục để relay audio. Toàn bộ gánh nặng đường truyền được đẩy sang cho Client và máy chủ OpenAI, Backend chỉ làm nhiệm vụ tạo token một lần duy nhất.
