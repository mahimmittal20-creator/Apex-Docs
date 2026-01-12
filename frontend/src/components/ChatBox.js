import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

function ChatBox({ resumeId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Load chat history when resumeId changes
  useEffect(() => {
    if (resumeId) {
      loadChatHistory();
    } else {
      setMessages([]);
    }
  }, [resumeId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/chat/${resumeId}`);
      setMessages(response.data);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !resumeId) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    // Optimistically add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await axios.post('http://localhost:8000/chat/', {
        resume_id: resumeId,
        message: userMessage
      });
      
      // Update with full history from server
      setMessages(response.data.chat_history);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    if (!resumeId) return;
    try {
      await axios.delete(`http://localhost:8000/chat/${resumeId}`);
      setMessages([]);
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  if (!resumeId) {
    return (
      <div className="chat-box disabled">
        <p>Generate a resume first to start chatting about it.</p>
      </div>
    );
  }

  return (
    <div className="chat-box">
      <div className="chat-header">
        <h3>💬 Ask about your resume</h3>
        {messages.length > 0 && (
          <button onClick={clearChat} className="clear-chat-btn">Clear Chat</button>
        )}
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-placeholder">
            <p>Ask me anything about your resume!</p>
            <p className="suggestions">Try: "How can I improve my summary?" or "What skills should I highlight?"</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <span className="message-role">{msg.role === 'user' ? 'You' : 'AI'}:</span>
            <span className="message-content">{msg.content}</span>
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant loading">
            <span className="message-role">AI:</span>
            <span className="message-content">Thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={sendMessage} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your resume..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatBox;

