import React, { useRef, useEffect } from 'react';
import { useChat } from './ChatProvider';
import { MessageBubble } from './MessageBubble';
import styles from './styles.module.css';

export const MessageList: React.FC = () => {
  const { messages, isLoading, error } = useChat();
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className={styles.messageList}>
      {messages.length === 0 && !isLoading && (
        <div style={{ textAlign: 'center', color: '#888', marginTop: '20%' }}>
          <h3>Welcome to AI Chat</h3>
          <p>Ask anything about the book or RAG system.</p>
        </div>
      )}
      
      {messages.map(msg => (
        <MessageBubble key={msg.id} message={msg} />
      ))}

      {isLoading && (
         <div className={`${styles.bubbleWrapper} ${styles.botWrapper}`}>
            <div className={`${styles.bubble} ${styles.botBubble}`} style={{opacity: 0.7}}>
                Thinking...
            </div>
         </div>
      )}

      {error && (
        <div style={{ color: 'red', textAlign: 'center', padding: '10px' }}>
          {error}
        </div>
      )}
      
      <div ref={endRef} />
    </div>
  );
};
