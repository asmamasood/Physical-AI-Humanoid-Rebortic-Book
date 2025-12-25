import React from 'react';
import { useChat } from './ChatProvider';
import styles from './styles.module.css';

export const HistorySidebar: React.FC = () => {
  const { 
    history, currentThreadId, loadThread, createNewThread, 
    agents, selectedAgentId, setSelectedAgent 
  } = useChat();

  return (
    <div className={styles.sidebar}>
      <div className={styles.sidebarHeader}>
        <strong>My Tutors</strong>
      </div>
      <div className={styles.agentList}>
        <div 
          className={`${styles.agentItem} ${selectedAgentId === null ? styles.activeAgent : ''}`}
          onClick={() => setSelectedAgent(null)}
        >
          <span className={styles.agentIcon}>🏫</span>
          <span className={styles.agentName}>Default Tutor</span>
        </div>
        {agents.map(agent => (
          <div 
            key={agent.id} 
            className={`${styles.agentItem} ${selectedAgentId === agent.id ? styles.activeAgent : ''}`}
            onClick={() => setSelectedAgent(agent.id)}
          >
            <span className={styles.agentIcon}>🤖</span>
            <div className={styles.agentMeta}>
              <span className={styles.agentName}>{agent.name}</span>
            </div>
          </div>
        ))}
      </div>

      <div className={styles.sidebarHeader} style={{ marginTop: '1rem', borderTop: '1px solid var(--ifm-color-emphasis-200)', paddingTop: '1rem' }}>
        <strong>History</strong>
        <button className={styles.newChatBtn} onClick={createNewThread}>+ New</button>
      </div>
      <div className={styles.threadList}>
        {history.map(thread => (
          <div 
            key={thread.id} 
            className={`${styles.threadItem} ${thread.id === currentThreadId ? styles.activeThread : ''}`}
            onClick={() => loadThread(thread.id)}
          >
            {thread.title || 'Untitled Chat'}
          </div>
        ))}
      </div>
    </div>
  );
};
