import React from 'react';
import { ChatProvider } from './ChatProvider';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { HistorySidebar } from './HistorySidebar';
import styles from './styles.module.css';

// The main view (inner)
const ChatKitView: React.FC<{ sidebarOpen?: boolean }> = ({ sidebarOpen = true }) => {
  return (
    <div className={styles.container}>
      {sidebarOpen && <HistorySidebar />}
      <div className={styles.mainArea}>
        <MessageList />
        <MessageInput />
      </div>
    </div>
  );
};

// The Public Wrapper
export const ChatKit: React.FC<{ sidebarOpen?: boolean }> = (props) => {
  return (
    <ChatProvider>
      <ChatKitView {...props} />
    </ChatProvider>
  );
};
