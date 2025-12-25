/**
 * API client for RAG Chatboard.
 * 
 * Provides functions to communicate with the backend API.
 */

// API base URL - uses environment variable or localhost for development
const API_BASE = typeof window !== 'undefined'
    ? (window.__RAG_API_BASE__ || 'http://localhost:8001/api')
    : 'http://localhost:8001/api';

/**
 * General chat request - uses RAG retrieval from Qdrant.
 * 
 * @param {string} query - User's question
 * @param {number} topK - Number of chunks to retrieve (default: 5)
 * @param {string} sessionId - Optional session ID for tracking
 * @param {string} userId - Optional user ID for history
 * @returns {Promise<{answer: string, citations: Array, session_id: string}>}
 */
export async function generalChat(query, topK = 5, sessionId = null, userId = null, moduleId = null, chapterId = null) {
    const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query,
            top_k: topK,
            session_id: sessionId,
            user_id: userId,
            module_id: moduleId,
            chapter_id: chapterId
        }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || 'Chat request failed');
    }

    return response.json();
}

/**
 * Selective chat request - answers ONLY from provided selection text.
 * 
 * Does NOT query Qdrant - strict selection-only mode.
 * 
 * @param {string} query - User's question about the selection
 * @param {string} selectionText - The highlighted text to answer from
 * @param {Object} selectionMeta - Optional metadata (url, element_id)
 * @param {string} sessionId - Optional session ID for tracking
 * @param {string} userId - Optional user ID for history
 * @returns {Promise<{answer: string, citations: Array, session_id: string}>}
 */
export async function selectiveChat(query, selectionText, selectionMeta = null, sessionId = null, userId = null) {
    const response = await fetch(`${API_BASE}/selective-chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query,
            selection_text: selectionText,
            selection_meta: selectionMeta,
            session_id: sessionId,
            user_id: userId,
        }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || 'Selective chat request failed');
    }

    return response.json();
}

/**
 * Get API metadata.
 * 
 * @returns {Promise<{version: string, collection: string, vectors_count: number}>}
 */
export async function getMeta() {
    const response = await fetch(`${API_BASE}/meta`, {
        method: 'GET',
    });

    if (!response.ok) {
        throw new Error('Failed to get metadata');
    }

    return response.json();
}

/**
 * Submit feedback for a chat response.
 * 
 * @param {string} sessionId - Session ID
 * @param {string} messageId - Message ID being rated
 * @param {number} rating - Rating from 1-5
 * @param {string} comment - Optional comment
 * @returns {Promise<{status: string}>}
 */
export async function submitFeedback(sessionId, messageId, rating, comment = null) {
    const response = await fetch(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            message_id: messageId,
            rating,
            comment,
        }),
    });

    if (!response.ok) {
        throw new Error('Failed to submit feedback');
    }

    return response.json();
}
/**
 * Get all chat threads for a user.
 * 
 * @param {string} userId - User ID
 * @returns {Promise<{threads: Array}>}
 */
export async function getChatHistory(userId) {
    const response = await fetch(`${API_BASE}/chat/history?user_id=${userId}`, {
        method: 'GET',
    });

    if (!response.ok) {
        throw new Error('Failed to fetch chat history');
    }

    return response.json();
}

/**
 * Get all messages for a specific thread.
 * 
 * @param {string} threadId - Thread ID
 * @param {string} userId - User ID
 * @returns {Promise<Array>}
 */
export async function getThreadMessages(threadId, userId) {
    const response = await fetch(`${API_BASE}/chat/history/${threadId}/messages?user_id=${userId}`, {
        method: 'GET',
    });

    if (!response.ok) {
        throw new Error('Failed to fetch thread messages');
    }

    return response.json();
}

/**
 * Delete a chat thread.
 * 
 * @param {string} threadId - Thread ID
 * @param {string} userId - User ID
 * @returns {Promise<{status: string}>}
 */
export async function deleteThread(threadId, userId) {
    const response = await fetch(`${API_BASE}/chat/history/${threadId}?user_id=${userId}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        throw new Error('Failed to delete thread');
    }

    return response.json();
}
/**
 * Translate text to Urdu.
 * 
 * @param {string} text - Text to translate
 * @returns {Promise<{translated_text: string}>}
 */
export async function translateText(text) {
    const response = await fetch(`${API_BASE}/translate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
    });

    if (!response.ok) {
        throw new Error('Translation failed');
    }

    return response.json();
}
