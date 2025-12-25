// frontend/rag-chat-plugin/src/utils/highlight.js

/**
 * Utility functions for handling text highlighting in Docusaurus.
 */

// Function to get the currently selected text
export function getSelectedText() {
  if (typeof window === 'undefined') {
    return ''; // Return empty string if not in browser environment
  }
  const selection = window.getSelection();
  return selection ? selection.toString().trim() : '';
}

// Function to get the range of the current selection (useful for positioning UI)
export function getSelectionRange() {
  if (typeof window === 'undefined') {
    return null;
  }
  const selection = window.getSelection();
  if (selection && selection.rangeCount > 0) {
    return selection.getRangeAt(0);
  }
  return null;
}

// Function to check if there is an active text selection
export function hasSelection() {
  return getSelectedText().length > 0;
}

// Optional: Function to clear the current selection
export function clearSelection() {
  if (typeof window !== 'undefined' && window.getSelection) {
    const selection = window.getSelection();
    if (selection) {
      selection.removeAllRanges();
    }
  }
}

// Optional: Function to get basic metadata about the selection's location
export function getSelectionMetadata() {
  if (typeof window === 'undefined' || !window.getSelection || window.getSelection().rangeCount === 0) {
    return null;
  }
  const range = window.getSelection().getRangeAt(0);
  const { startContainer, endContainer, startOffset, endOffset } = range;

  // Attempt to find a parent element with an ID or a data-id to use as a locator
  let parentId = null;
  let currentElement = startContainer.nodeType === Node.ELEMENT_NODE ? startContainer : startContainer.parentElement;

  while (currentElement && currentElement !== document.body) {
    if (currentElement.id) {
      parentId = currentElement.id;
      break;
    }
    // Docusaurus often uses data-mdx-content for content blocks
    if (currentElement.dataset && currentElement.dataset.mdxContent) {
      parentId = 'mdx-content'; // Generic identifier for the content block
      break;
    }
    currentElement = currentElement.parentElement;
  }

  return {
    parentId: parentId,
    startOffset: startOffset,
    endOffset: endOffset,
    // Add other relevant info like page URL, module/chapter from Docusaurus context if available
    url: window.location.href,
  };
}
