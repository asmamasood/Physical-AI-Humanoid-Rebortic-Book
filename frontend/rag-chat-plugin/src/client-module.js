// frontend/rag-chat-plugin/src/client-module.js
import React from 'react';
import { createRoot } from 'react-dom/client';
import ChatWindow from './components/ChatWindow';
import HighlightMenu from './components/components/HighlightMenu';

export default function clientModule() {
  if (typeof document !== 'undefined') {
    window.addEventListener('load', () => {
      // Find the root element where the chat window will be mounted
      let chatRoot = document.getElementById('rag-chat-root');
      if (!chatRoot) {
        chatRoot = document.createElement('div');
        chatRoot.id = 'rag-chat-root';
        document.body.appendChild(chatRoot);
      }
      
      const root = createRoot(chatRoot);
      root.render(
        <React.StrictMode>
          <ChatWindow />
          {/* HighlightMenu is designed to portal itself to document.body,
              so it doesn't strictly need to be rendered here in the same root,
              but rendering it here ensures it's part of the React tree and hooks */}
          <HighlightMenu />
        </React.StrictMode>
      );
    });
  }
}
