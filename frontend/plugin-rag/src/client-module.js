/**
 * Client module for RAG Chatboard.
 * 
 * Injects the ChatBoard React component into the DOM on page load.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import ChatBoard from './components/ChatBoard';

/**
 * Initialize the ChatBoard component.
 */
function initChatBoard() {
    if (typeof document === 'undefined') return;

    // Check if chat is enabled via Docusaurus config
    const chatEnabled = window.__DOCUSAURUS__?.customFields?.chatEnabled ?? true;
    if (!chatEnabled) {
        console.log('RAG Chatboard: disabled via config');
        return;
    }

    // Restriction: Only show on book pages (docs)
    if (!window.location.pathname.startsWith('/docs/')) {
        return;
    }

    // Find or create root element
    let chatRoot = document.getElementById('rag-chatboard-root');
    if (!chatRoot) {
        chatRoot = document.createElement('div');
        chatRoot.id = 'rag-chatboard-root';
        document.body.appendChild(chatRoot);

        // Render ChatBoard only when we create the root
        const root = createRoot(chatRoot);
        root.render(
            <React.StrictMode>
                <ChatBoard />
            </React.StrictMode>
        );
        console.log('RAG Chatboard: mounted');
    }
}

/**
 * Remove the ChatBoard component.
 */
function cleanupChatBoard() {
    const chatRoot = document.getElementById('rag-chatboard-root');
    if (chatRoot) {
        chatRoot.remove();
        console.log('RAG Chatboard: unmounted');
    }
}

/**
 * Handle route updates.
 */
export function onRouteUpdate({ location }) {
    // Disabled - now handled by Root.tsx for better context support
}

// Initialize on DOM ready (initial load) - Disabled
/*
if (typeof window !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
...
*/

export default initChatBoard;
