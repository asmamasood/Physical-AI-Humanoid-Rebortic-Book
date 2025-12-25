import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from './types';
import styles from './styles.module.css'; // We'll create this later

interface Props {
  message: Message;
}

export const MessageBubble: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`${styles.bubbleWrapper} ${isUser ? styles.userWrapper : styles.botWrapper}`}>
      {!isUser && message.agent_name && (
        <div className={styles.agentNameLabel}>{message.agent_name}</div>
      )}
      <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.botBubble}`}>
        {isUser ? (
          <div className={styles.text}>{message.content}</div>
        ) : (
          <div className={styles.markdown}>
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};
