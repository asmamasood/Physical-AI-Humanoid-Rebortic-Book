// frontend/rag-chat-plugin/src/components/ChatWindow.jsx
import React, { useState, useEffect, useRef } from 'react';
import { generalChat, selectiveChat } from '../api/chat'; // Assuming selectiveChat is exported from chat.js
import HighlightMenu from './HighlightMenu'; // Import the HighlightMenu
import styles from './ChatWindow.module.css'; // Assuming you'll create a CSS module for ChatWindow

const ChatWindow = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState(() => {
    if (typeof window !== 'undefined') {
      const savedMessages = localStorage.getItem('chatHistory');
      return savedMessages ? JSON.parse(savedMessages) : [];
    }
    return [];
  });
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chatHistory', JSON.stringify(messages));
    }
  }, [messages]);

  // Function to handle selective chat response from HighlightMenu
  const handleSelectiveChatResponse = (response) => {
    if (response.error) {
      setMessages((prevMessages) => [...prevMessages, { type: 'bot', text: response.error }]);
    } else {
      setMessages((prevMessages) => [...prevMessages, { type: 'bot', text: response.answer, citations: response.citations }]);
    }
    setIsOpen(true); // Open chat window to show response
    setIsLoading(false);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleToggleChat = () => {
      setIsOpen((prevIsOpen) => !prevIsOpen);
    };

    window.addEventListener('toggleChatWindow', handleToggleChat);

    return () => {
      window.removeEventListener('toggleChatWindow', handleToggleChat);
    };
  }, []);

  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    const userMessage = { type: 'user', text: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await generalChat(input);
      setMessages((prevMessages) => [...prevMessages, { type: 'bot', text: response.answer, citations: response.citations }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prevMessages) => [...prevMessages, { type: 'bot', text: 'Sorry, something went wrong. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = () => {
    setMessages([]);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('chatHistory');
    }
  };

  return (
    <>
      <HighlightMenu onSelectiveChatResponse={handleSelectiveChatResponse} /> {/* Render the HighlightMenu */}

      {!isOpen && (
        <button className={styles.chatToggleButton} onClick={() => setIsOpen(true)}>
          💬
        </button>
      )}

      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.chatHeader}>
            <span>RAG Chatboard</span>
            <div>
              <button onClick={handleClearHistory} title="Clear History">
                🗑️
              </button>
              <button onClick={() => setIsOpen(false)} title="Close Chat">
                ✕
              </button>
            </div>
          </div>
          <div className={styles.chatMessages}>
            {messages.map((msg, index) => (
              <div key={index} className={`${styles.message} ${styles[msg.type]}`}>
                <p>{msg.text}</p>
                {msg.citations && msg.citations.length > 0 && (
                  <div className={styles.citations}>
                    <strong>Citations:</strong>
                    <ul>
                      {msg.citations.map((citation, idx) => (
                        <li key={idx}>
                          <a href={citation.url} target="_blank" rel="noopener noreferrer">
                            {citation.title || `Source ${idx + 1}`}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className={`${styles.message} ${styles.bot}`}>
                <p>Thinking...</p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <div className={styles.chatInputContainer}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage();
                }
              }}
              placeholder="Ask me anything about the book..."
              disabled={isLoading}
            />
            <button onClick={handleSendMessage} disabled={isLoading}>
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatWindow;

