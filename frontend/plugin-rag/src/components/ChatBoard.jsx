import React, { useState, useEffect, useRef, useCallback } from 'react';
import { generalChat, selectiveChat, getChatHistory, getThreadMessages, deleteThread, translateText } from '../api/chat';
import HighlightButton from './HighlightButton';
import styles from './ChatBoard.module.css';

// Try to use session if available (Project uses Better Auth)
// Since this is a plugin, we need to be careful about imports.
// In the project structure, auth-client is at src/lib/auth-client.ts
import { useSession } from '../../../../physical-ai-robotics-book/src/lib/auth-client';

function generateId() {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export default function ChatBoard({ isInline = false }) {
    const { data: session } = useSession();
    const [isOpen, setIsOpen] = useState(isInline); // Open by default if inline
    const [showHistory, setShowHistory] = useState(false);
    const [threads, setThreads] = useState([]);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [activeThreadId, setActiveThreadId] = useState(null);

    const [selectionText, setSelectionText] = useState('');
    const [selectionPosition, setSelectionPosition] = useState({ top: 0, left: 0 });

    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Keep open if inline
    useEffect(() => {
        if (isInline && !isOpen) {
            setIsOpen(true);
        }
    }, [isInline, isOpen]);

    // Load History if logged in
    useEffect(() => {
        if (session?.user?.id && isOpen) {
            loadHistory(true); // Pass true to auto-select latest thread on first load
        }
    }, [session, isOpen]);

    const loadHistory = async (autoSelectLatest = false) => {
        try {
            const data = await getChatHistory(session.user.id);
            const loadedThreads = data.threads || [];
            setThreads(loadedThreads);

            // Auto-select latest thread if requested and none is active
            if (autoSelectLatest && loadedThreads.length > 0 && !activeThreadId) {
                handleSwitchThread(loadedThreads[0].id);
            }
        } catch (err) {
            console.error('Failed to load history:', err);
        }
    };

    const handleSwitchThread = async (threadId) => {
        setIsLoading(true);
        setActiveThreadId(threadId);
        setShowHistory(false);
        try {
            const msgs = await getThreadMessages(threadId, session.user.id);
            // Convert DB roles to Chat roles
            setMessages(msgs.map(m => ({
                id: m.id,
                role: m.role,
                content: m.content
            })));
        } catch (err) {
            console.error('Failed to load thread messages:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleNewChat = () => {
        setActiveThreadId(`session_${Date.now()}`);
        setMessages([]);
        setShowHistory(false);
    };

    const handleDeleteThread = async (e, threadId) => {
        e.stopPropagation();
        try {
            await deleteThread(threadId, session.user.id);
            setThreads(prev => prev.filter(t => t.id !== threadId));
            if (activeThreadId === threadId) {
                handleNewChat();
            }
        } catch (err) {
            console.error('Failed to delete thread:', err);
        }
    };

    const handleTranslate = async (messageId, text) => {
        try {
            const data = await translateText(text);
            setMessages(prev => prev.map(m =>
                m.id === messageId ? { ...m, content: data.translated_text, isUrdu: true } : m
            ));
        } catch (err) {
            console.error('Translation error:', err);
        }
    };

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        if (isOpen) {
            inputRef.current?.focus();
        }
    }, [isOpen]);

    useEffect(() => {
        if (typeof window === 'undefined') return;

        const handleMouseUp = () => {
            const selection = window.getSelection();
            const text = selection?.toString().trim();

            if (text && text.length > 20) {
                const range = selection.getRangeAt(0);
                const rect = range.getBoundingClientRect();

                setSelectionText(text);
                setSelectionPosition({
                    top: rect.top + window.scrollY - 45,
                    left: rect.left + window.scrollX + (rect.width / 2),
                });
            } else {
                setSelectionText('');
            }
        };

        const handleMouseDown = (e) => {
            if (!e.target.closest('[data-highlight-button]')) {
                setSelectionText('');
            }
        };

        document.addEventListener('mouseup', handleMouseUp);
        document.addEventListener('mousedown', handleMouseDown);

        return () => {
            document.removeEventListener('mouseup', handleMouseUp);
            document.removeEventListener('mousedown', handleMouseDown);
        };
    }, []);

    useEffect(() => {
        if (typeof window === 'undefined') return;
        const handleToggle = () => setIsOpen((prev) => !prev);
        window.addEventListener('toggleChatWindow', handleToggle);
        return () => window.removeEventListener('toggleChatWindow', handleToggle);
    }, []);

    const handleSend = useCallback(async () => {
        if (!input.trim() || isLoading) return;

        const userMsg = { id: generateId(), role: 'user', content: input.trim() };
        setMessages((prev) => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            // Use activeThreadId as session_id for backend
            const threadIdToUse = activeThreadId || `session_${Date.now()}`;
            if (!activeThreadId) setActiveThreadId(threadIdToUse);

            const response = await generalChat(input.trim(), 5, threadIdToUse, session?.user?.id);

            const assistantMsg = {
                id: generateId(),
                role: 'assistant',
                content: response.answer,
                citations: response.citations || [],
            };

            setMessages((prev) => [...prev, assistantMsg]);
            if (session?.user?.id) loadHistory(); // Refresh threads list
        } catch (error) {
            console.error('Chat error:', error);
            setMessages((prev) => [...prev, {
                id: generateId(),
                role: 'assistant',
                content: 'Sorry, something went wrong. Please try again.',
                isError: true,
            }]);
        } finally {
            setIsLoading(false);
        }
    }, [input, isLoading, activeThreadId, session]);

    const handleAskSelection = useCallback(async () => {
        if (!selectionText || isLoading) return;
        setIsOpen(true);
        setIsLoading(true);

        const userMsg = {
            id: generateId(),
            role: 'user',
            content: `[About selection] "${selectionText.slice(0, 100)}${selectionText.length > 100 ? '...' : ''}"`,
            isSelection: true,
        };
        setMessages((prev) => [...prev, userMsg]);

        try {
            const threadIdToUse = activeThreadId || `session_${Date.now()}`;
            if (!activeThreadId) setActiveThreadId(threadIdToUse);

            const response = await selectiveChat(
                'Explain this text in detail',
                selectionText,
                { url: window.location.href },
                threadIdToUse,
                session?.user?.id
            );

            const assistantMsg = {
                id: generateId(),
                role: 'assistant',
                content: response.answer,
                citations: response.citations || [],
            };
            setMessages((prev) => [...prev, assistantMsg]);
        } catch (error) {
            console.error('Selective chat error:', error);
            setMessages((prev) => [...prev, {
                id: generateId(),
                role: 'assistant',
                content: 'Sorry, I couldn\'t process your selection.',
                isError: true,
            }]);
        } finally {
            setIsLoading(false);
            setSelectionText('');
        }
    }, [selectionText, isLoading, activeThreadId, session]);

    return (
        <>
            {selectionText && (
                <HighlightButton position={selectionPosition} onClick={handleAskSelection} disabled={isLoading} />
            )}

            {!isOpen && !isInline && (
                <button className={styles.toggleButton} onClick={() => setIsOpen(true)}>💬</button>
            )}

            {isOpen && (
                <div className={`${styles.chatWindow} ${isInline ? styles.inline : ''}`}>
                    <div className={styles.header}>
                        <div className={styles.headerTitle}>
                            <button
                                onClick={() => setShowHistory(!showHistory)}
                                className={styles.historyToggle}
                                title="Toggle Chat History"
                            >
                                📜
                            </button>
                            <span>AI Assistant</span>
                        </div>
                        <div className={styles.headerButtons}>
                            <button onClick={handleNewChat} title="New Chat" className={styles.headerButton}>➕</button>
                            {!isInline && <button onClick={() => setIsOpen(false)} title="Close chat" className={styles.headerButton}>✕</button>}
                        </div>
                    </div>

                    <div className={styles.skillsBar}>
                        <button className={styles.skillChip} onClick={() => setInput("Summarize this page 📖")}>Summarize 📖</button>
                        <button className={styles.skillChip} onClick={() => setInput("Quiz me on this content 🎯")}>Quiz 🎯</button>
                    </div>

                    <div className={styles.mainContent}>
                        {showHistory && (
                            <div className={styles.historySidebar}>
                                <h3>Previous Conversations</h3>
                                {threads.length === 0 ? (
                                    <p className={styles.emptyHint}>No history yet.</p>
                                ) : (
                                    <div className={styles.threadList}>
                                        {threads.map(t => (
                                            <div
                                                key={t.id}
                                                className={`${styles.threadItem} ${activeThreadId === t.id ? styles.activeThread : ''}`}
                                                onClick={() => handleSwitchThread(t.id)}
                                            >
                                                <span className={styles.threadTitle}>{t.title || 'Untitled Chat'}</span>
                                                <button
                                                    className={styles.deleteThread}
                                                    onClick={(e) => handleDeleteThread(e, t.id)}
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        <div className={styles.chatArea}>
                            <div className={styles.messages}>
                                {messages.length === 0 && (
                                    <div className={styles.emptyState}>
                                        <p>👋 Hello! Ask me anything about the book.</p>
                                        {!session && <p className={styles.loginHint}>Sign in to save your chat history!</p>}
                                    </div>
                                )}

                                {messages.map((msg) => (
                                    <div key={msg.id} className={`${styles.message} ${styles[msg.role]} ${msg.isError ? styles.error : ''} ${msg.isUrdu ? styles.urdu : ''}`}>
                                        <div className={styles.messageContent}>{msg.content}</div>
                                        {msg.role === 'assistant' && !msg.isError && !msg.isUrdu && (
                                            <button
                                                className={styles.translateButton}
                                                onClick={() => handleTranslate(msg.id, msg.content)}
                                                title="Translate to Urdu"
                                            >
                                                🇵🇰 Translate
                                            </button>
                                        )}
                                        {msg.citations?.length > 0 && (
                                            <div className={styles.citations}>
                                                {msg.citations.map((c, i) => (
                                                    <a key={i} href={c.source_url} target="_blank" className={styles.citation}>
                                                        {c.module}:{c.chapter}
                                                    </a>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ))}
                                {isLoading && <div className={`${styles.message} ${styles.assistant}`}><div className={styles.loading}><span></span><span></span><span></span></div></div>}
                                <div ref={messagesEndRef} />
                            </div>

                            <div className={styles.inputArea}>
                                <input
                                    ref={inputRef}
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="Ask about the book..."
                                    disabled={isLoading}
                                    className={styles.input}
                                />
                                <button onClick={handleSend} disabled={isLoading || !input.trim()} className={styles.sendButton}>
                                    Send
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
