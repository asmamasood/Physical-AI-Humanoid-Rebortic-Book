// physical-ai-robotics-book/src/theme/NavbarItem/ChatButton.jsx
import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

const ChatButton = () => {
  const {
    siteConfig: { customFields },
  } = useDocusaurusContext();

  const chatEnabled = customFields?.chatEnabled || false;

  if (!chatEnabled) {
    return null;
  }

  const handleClick = () => {
    // This will toggle the visibility of the ChatWindow via global state or direct DOM manipulation
    // For simplicity, we can assume the ChatWindow component itself handles its visibility state
    // and this button might trigger a global event or a specific function on the window object.
    // In a more complex setup, you'd use React Context or a global state manager.
    // For now, we'll just log and assume the ChatWindow will react.
    console.log('Chat button clicked!');
    // Example: dispatch a custom event that ChatWindow listens to
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('toggleChatWindow'));
    }
  };

  return (
    <button
      className="button button--secondary navbar-item-control"
      onClick={handleClick}
      title="Toggle RAG Chat"
      aria-label="Toggle RAG Chat"
    >
      💬 Chat
    </button>
  );
};

export default ChatButton;
