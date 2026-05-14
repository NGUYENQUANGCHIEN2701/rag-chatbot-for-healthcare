# BÁO CÁO: TÍCH HỢP TÍNH NĂNG "AI VOICE KHẨN CẤP" (REALTIME WEBRTC)

## 1. MỤC TIÊU VÀ BỐI CẢNH
Hệ thống RAG Chatbot Y tế được bổ sung thêm một tính năng chuyên biệt dành riêng cho trường hợp khẩn cấp: **Sơ cấp cứu bệnh nhân ngất xỉu**. 
Trong tình huống này, người dùng thường rơi vào trạng thái hoảng loạn, hai tay bận rộn để thao tác trên cơ thể người bệnh. Do đó, phương thức chat bằng văn bản truyền thống (Text-based UI) không còn hiệu quả. 
=> Giải pháp: Tích hợp chức năng Voice AI tương tác thời gian thực (Full-duplex Realtime) như một người đồng hành trực tuyến, tự động lắng nghe và phát lại giọng nói mà không cần người dùng thao tác thiết bị.

## 2. KIẾN TRÚC HỆ THỐNG
Hệ thống sử dụng kiến trúc **Client-Server-LLM** kết hợp giao thức **WebRTC** để giảm thiểu độ trễ (latency < 500ms).

*   **Frontend (React/Vite)**: Chịu trách nhiệm mở Microphone, hiển thị giao diện khẩn cấp trực quan và tạo kết nối WebRTC (Peer-to-Peer) thẳng đến máy chủ OpenAI.
*   **Backend (FastAPI)**: Đóng vai trò là "Cổng bảo mật" (Security Gate). Thay vì làm Proxy chuyển tiếp âm thanh (gây tăng độ trễ), Backend chịu trách nhiệm tạo và quản lý Session tạm thời (Ephemeral Token) từ OpenAI, đồng thời nạp (inject) Kịch bản Prompt khẩn cấp.
*   **LLM (OpenAI Realtime API - `gpt-4o-mini-realtime-preview`)**: Xử lý luồng âm thanh trực tiếp từ người dùng, nhận diện giọng nói (STT), suy luận theo Prompt (LLM), và tổng hợp giọng nói (TTS) trả về cùng lúc.

## 3. LUỒNG HOẠT ĐỘNG (FLOW)

Dưới đây là luồng hoạt động từng bước từ khi người dùng bấm nút "CẤP CỨU":

1. **Khởi tạo (Initialization):**
   * Người dùng bấm nút **🚨 CẤP CỨU** trên Frontend.
   * Giao diện `EmergencyMode` (Overlay) hiển thị toàn màn hình, chặn mọi thao tác chat văn bản thông thường.
2. **Xin Cấp quyền (Token Request):**
   * Frontend gọi API `GET /api/voice-token` trên Backend.
   * Backend dùng thư viện `requests` gọi lên OpenAI API (`/v1/realtime/sessions`) với API Key gốc.
   * Backend truyền kèm một **System Instruction** cực kỳ khắt khe: Bắt buộc AI phải thấu cảm, nói rất ngắn (1-2 câu), và chỉ yêu cầu 1 thao tác mỗi lần.
   * OpenAI trả về `client_secret` (Ephemeral Token - có giá trị sử dụng một lần trong thời gian ngắn). Backend gửi Token này về cho Frontend.
3. **Kết nối WebRTC (Connection Setup):**
   * Frontend tạo đối tượng `RTCPeerConnection`.
   * Frontend lấy luồng âm thanh từ Microphone (nhờ `navigator.mediaDevices.getUserMedia`) và gắn vào PeerConnection.
   * Frontend dùng Ephemeral Token vừa nhận để gửi Session Description Protocol (SDP) Offer trực tiếp đến OpenAI Realtime URL.
   * OpenAI phản hồi SDP Answer. Kết nối WebRTC (Peer-to-Peer) được thiết lập.
4. **Tương tác Thời gian thực (Full-duplex Interaction):**
   * Người dùng nói -> Luồng âm thanh được đẩy thẳng đến OpenAI qua WebRTC.
   * Nhờ công nghệ **Server VAD (Voice Activity Detection)**, OpenAI tự động nhận biết lúc nào người dùng ngừng nói để bắt đầu xử lý.
   * Nếu AI đang nói (hướng dẫn ép tim) mà người dùng hốt hoảng la lên *"Anh ấy tỉnh rồi!"*, tính năng Interruption (ngắt lời) của Realtime API sẽ ngay lập tức cắt ngang âm thanh của AI và xử lý câu nói mới của người dùng.
5. **Kết thúc (Termination):**
   * Người dùng nhấn "Kết thúc cuộc gọi".
   * Frontend giải phóng Microphone (`stream.getTracks().stop()`) và đóng PeerConnection (`pc.close()`).

## 4. TỐI ƯU HÓA TRẢI NGHIỆM (UX/UI & PROMPT)

*   **UI - Xóa bỏ rào cản**: Giao diện cấp cứu hiển thị Overlay che toàn bộ website để tập trung tuyệt đối. Có vòng tròn hiệu ứng sóng âm đập theo nhịp (Pulsing Animation) để tạo cảm giác "AI vẫn đang lắng nghe" nhưng không chiếm sự chú ý.
*   **Prompt Engineering - Kịch bản thấu cảm**: Prompt đã được điều chỉnh từ dạng cứng ngắc sang dạng "người bạn đồng hành". Các chỉ thị cụ thể:
    *   Trấn an ngay từ đầu: "Bình tĩnh nhé, có tôi ở đây".
    *   Hỏi và Đợi: Hướng dẫn xong phải bắt buộc hỏi "Bạn làm xong chưa?".
    *   Chia nhỏ hành động: Thay vì quăng nguyên quy trình CPR, AI sẽ hỏi "Lồng ngực có thở không?" -> Đợi nghe -> Nếu không thì mới chỉ cách ép tim.

## 5. TỔNG KẾT
Việc chuyển đổi từ WebSocket Proxy sang WebRTC trực tiếp thông qua Ephemeral Token mang lại 2 lợi ích cốt lõi:
1. **Độ trễ siêu thấp**: Cực kỳ quan trọng trong sơ cấp cứu "thời gian là vàng".
2. **Tiết kiệm tài nguyên máy chủ**: Backend không phải mở hàng chục luồng WebSocket liên tục để nhận và đẩy audio, toàn bộ gánh nặng đường truyền được đẩy sang cho Client và máy chủ OpenAI.
