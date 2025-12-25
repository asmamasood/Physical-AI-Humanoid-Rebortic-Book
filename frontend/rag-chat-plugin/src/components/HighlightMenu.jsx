// frontend/rag-chat-plugin/src/components/HighlightMenu.jsx
import React, { useState, useEffect, useRef } from 'react';
import ReactDOM from 'react-dom';
import { getSelectedText, getSelectionMetadata, hasSelection, clearSelection } from '../utils/highlight';
import { selectiveChat } from '../api/chat'; // Assuming selectiveChat is exported from chat.js
import styles from './HighlightMenu.module.css'; // For styling

const HighlightMenu = ({ onSelectiveChatResponse }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const menuRef = useRef(null);
  const selectedTextRef = useRef(''); // To store the selected text
  const selectionMetaRef = useRef(null); // To store selection metadata

  const handleSelection = () => {
    if (typeof window === 'undefined') return;

    const currentSelection = getSelectedText();
    const currentMeta = getSelectionMetadata();

    if (hasSelection() && !isVisible) {
      const range = window.getSelection().getRangeAt(0);
      const rect = range.getBoundingClientRect();
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

      setPosition({
        top: rect.top + scrollTop - 40, // Position above the selection
        left: rect.left + scrollLeft + (rect.width / 2) - 50, // Center above selection
      });
      selectedTextRef.current = currentSelection;
      selectionMetaRef.current = currentMeta;
      setIsVisible(true);
    } else if (!hasSelection() && isVisible) {
      setIsVisible(false);
      selectedTextRef.current = '';
      selectionMetaRef.current = null;
    }
  };

  const handleAskChatboard = async () => {
    if (selectedTextRef.current) {
      setIsVisible(false); // Hide menu immediately
      clearSelection(); // Clear selection after action

      try {
        // You might want to show a loading indicator here
        const response = await selectiveChat(selectedTextRef.current, selectionMetaRef.current);
        onSelectiveChatResponse(response); // Pass the response up to the parent component
      } catch (error) {
        console.error('Error during selective chat:', error);
        // Handle error, e.g., show an error message
        onSelectiveChatResponse({ error: 'Failed to get a response from the chatboard.' });
      }
    }
  };

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.addEventListener('mouseup', handleSelection);
      document.addEventListener('keyup', handleSelection); // For keyboard selections
      return () => {
        document.removeEventListener('mouseup', handleSelection);
        document.removeEventListener('keyup', handleSelection);
      };
    }
  }, [isVisible]); // Re-run effect when visibility changes to ensure correct event listener state

  if (!isVisible) {
    return null;
  }

  // Ensure the menu doesn't go off-screen
  const adjustedLeft = Math.max(0, position.left);

  return ReactDOM.createPortal(
    <div
      ref={menuRef}
      className={styles.highlightMenu}
      style={{ top: position.top, left: adjustedLeft }}
      onMouseDown={(e) => e.stopPropagation()} // Prevent selection clear when clicking menu
    >
      <button onClick={handleAskChatboard} className={styles.askButton}>
        Ask Chatboard
      </button>
    </div>,
    document.body // Portal to document.body to ensure it's on top
  );
};

export default HighlightMenu;
