import React, { useState, useEffect, useRef } from 'react';
import './EmergencyMode.css';

const EmergencyMode = ({ onClose }) => {
  const [status, setStatus] = useState('Khởi tạo...');
  const [isActive, setIsActive] = useState(false);
  const pcRef = useRef(null);
  const audioElRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    // Create audio element for playback
    const audioEl = document.createElement("audio");
    audioEl.autoplay = true;
    audioElRef.current = audioEl;

    startEmergencyCall();

    return () => {
      stopCall();
    };
  }, []);

  const startEmergencyCall = async () => {
    try {
      setStatus('Đang xin quyền Microphone...');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      setStatus('Đang kết nối y tế khẩn cấp...');
      
      // Get Ephemeral Token
      const tokenRes = await fetch('http://localhost:8000/api/voice-token');
      if (!tokenRes.ok) throw new Error('Cannot get voice token');
      const sessionData = await tokenRes.json();
      const ephemeralKey = sessionData.client_secret.value;

      // Setup WebRTC
      const pc = new RTCPeerConnection();
      pcRef.current = pc;

      // Play audio from OpenAI
      pc.ontrack = e => {
        if (audioElRef.current) {
          audioElRef.current.srcObject = e.streams[0];
        }
      };

      // Add local microphone to PC
      pc.addTrack(stream.getTracks()[0]);

      // Data channel for events
      const dc = pc.createDataChannel("oai-events");
      dc.addEventListener("message", (e) => {
        // You can handle OpenAI Realtime events here if needed
        console.log("Realtime event:", e.data);
      });

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const baseUrl = "https://api.openai.com/v1/realtime";
      const model = "gpt-4o-mini-realtime-preview-2024-12-17";
      const sdpResponse = await fetch(`${baseUrl}?model=${model}`, {
        method: "POST",
        body: offer.sdp,
        headers: {
          Authorization: `Bearer ${ephemeralKey}`,
          "Content-Type": "application/sdp"
        }
      });

      if (!sdpResponse.ok) {
        throw new Error('WebRTC connection failed');
      }

      const answer = {
        type: "answer",
        sdp: await sdpResponse.text(),
      };
      await pc.setRemoteDescription(answer);

      setStatus('Đang lắng nghe... Hãy nói tình trạng bệnh nhân!');
      setIsActive(true);

    } catch (error) {
      console.error(error);
      setStatus('Lỗi kết nối! Vui lòng gọi 115 ngay lập tức.');
    }
  };

  const stopCall = () => {
    if (pcRef.current) {
      pcRef.current.close();
      pcRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsActive(false);
  };

  return (
    <div className="emergency-overlay">
      <div className="emergency-container">
        <h2 className="emergency-title">CẤP CỨU NGẤT XỈU</h2>
        <div className={`pulsing-circle ${isActive ? 'active' : ''}`}>
          <div className="microphone-icon">
             <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="22"></line>
             </svg>
          </div>
        </div>
        <p className="emergency-status">{status}</p>
        <button className="end-call-btn" onClick={onClose}>
          Kết Thúc Cuộc Gọi
        </button>
      </div>
    </div>
  );
};

export default EmergencyMode;
