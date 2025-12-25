import React, { useState } from 'react';
import styles from './styles.module.css';
import { useSession } from '../../lib/auth-client';
import { ChatKit } from '../ChatKit';
import { useChat } from '../ChatKit/ChatProvider';

export default function FloatingChat() {
  const { data: session } = useSession();
  const [isOpen, setIsOpen] = useState(false);
  const { agents, selectedAgentId } = useChat();

  const selectedAgent = agents.find(a => a.id === selectedAgentId);
  const headerTitle = selectedAgent ? selectedAgent.name : 'AI Assistant';

  // Only show for authenticated users
  if (!session) return null;

  return (
    <div className={styles.floatingContainer}>
      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.header}>
            <span>{headerTitle}</span>
            <button 
              className={styles.closeBtn}
              onClick={() => setIsOpen(false)}
            >
              ×
            </button>
          </div>
          {/* Use the new ChatKit here, sidebar hidden for widget mode */}
          <div className={styles.chatBody}>
             <ChatKit sidebarOpen={false} />
          </div>
        </div>
      )}

      <button 
        className={styles.floatBtn}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle Chat"
      >
        💬
      </button>
    </div>
  );
}
