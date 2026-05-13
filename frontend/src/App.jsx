import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
// SVG Icons for no-dependency beauty
const SendIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"></line>
    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
  </svg>
);

const BotIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2v2"></path>
    <path d="M12 18v2"></path>
    <path d="M4.93 4.93l1.41 1.41"></path>
    <path d="M17.66 17.66l1.41 1.41"></path>
    <path d="M2 12h2"></path>
    <path d="M20 12h2"></path>
    <path d="M6.34 17.66l-1.41 1.41"></path>
    <path d="M19.07 4.93l-1.41 1.41"></path>
    <circle cx="12" cy="12" r="4"></circle>
  </svg>
);

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'bot',
      content: 'Xin chào! Tôi là trợ lý AI chuyên về lĩnh vực sơ cấp cứu. Bạn cần hỗ trợ gì hôm nay?',
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { id: Date.now(), role: 'user', content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: userMessage.content,
      });

      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: 'bot', content: response.data.answer },
      ]);
    } catch (error) {
      console.error('Error fetching chat:', error);
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: 'bot', content: 'Xin lỗi, đã có lỗi kết nối tới máy chủ. Vui lòng kiểm tra lại!' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="chat-wrapper">
        <header className="chat-header">
          <div className="bot-avatar">
            <BotIcon />
          </div>
          <div>
            <h1>Healthcare Assistant AI</h1>
            <p>Trợ lý sơ cấp cứu nội bộ</p>
          </div>
        </header>

        <div className="chat-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-row ${msg.role}`}>
              <div className="message-bubble">
                {msg.role === 'bot' ? (
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      a: ({node, ...props}) => <a target="_blank" rel="noopener noreferrer" style={{color: '#60a5fa', textDecoration: 'underline'}} {...props} />
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  msg.content.split('\n').map((line, i) => (
                    <span key={i}>
                      {line}
                      <br />
                    </span>
                  ))
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-row bot">
              <div className="message-bubble typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-container" onSubmit={handleSend}>
          <div className="chat-input-wrapper">
            <input
              type="text"
              className="chat-input"
              placeholder="Hỏi tôi về hướng dẫn sơ cấp cứu..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button type="submit" className="send-button" disabled={!input.trim() || isLoading}>
              <SendIcon />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
