import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useSession } from '../../lib/auth-client';
import { ChatContextType, Message, Thread, ChatState } from './types';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { data: session } = useSession();
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
    currentThreadId: null,
    history: [],
    agents: [],
    selectedAgentId: null,
  });

  const userId = session?.user?.id;

  // Load History on Mount
  const refreshHistory = useCallback(async () => {
    if (!userId) return;
    try {
      const res = await axios.get(`${API_BASE}/chat/history?user_id=${userId}`);
      setState(prev => ({ ...prev, history: res.data.threads }));
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  }, [userId]);

  const refreshAgents = useCallback(async () => {
    if (!userId) return;
    try {
      const res = await axios.get(`${API_BASE}/agents/${userId}`);
      setState(prev => ({ ...prev, agents: res.data || [] }));
    } catch (err) {
      console.error('Failed to load agents:', err);
    }
  }, [userId]);

  useEffect(() => {
    refreshHistory();
    refreshAgents();
  }, [refreshHistory, refreshAgents]);

  const loadThread = async (threadId: string) => {
    if (!userId) return;
    setState(prev => ({ ...prev, isLoading: true, currentThreadId: threadId }));
    try {
      const res = await axios.get(`${API_BASE}/chat/history/${threadId}/messages?user_id=${userId}`);
      setState(prev => ({ 
        ...prev, 
        messages: res.data, 
        isLoading: false,
        currentThreadId: threadId
      }));
    } catch (err) {
      setState(prev => ({ ...prev, isLoading: false, error: 'Failed to load thread' }));
    }
  };

  const createNewThread = () => {
    setState(prev => ({
      ...prev,
      messages: [],
      currentThreadId: null,
      error: null
    }));
  };

  const sendMessage = async (content: string) => {
    if (!userId) return;
    
    // Optimistic UI
    const tempUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content
    };
    
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, tempUserMsg],
      isLoading: true,
      error: null
    }));

    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        query: content,
        session_id: state.currentThreadId,
        user_id: userId,
        agent_id: state.selectedAgentId
      });

      const selectedAgent = state.agents.find(a => a.id === state.selectedAgentId);
      const botMsg: Message = {
        id: Date.now().toString() + '_bot',
        role: 'assistant',
        content: res.data.answer,
        agent_name: selectedAgent?.name
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, botMsg],
        isLoading: false,
        currentThreadId: res.data.session_id
      }));

      if (!state.currentThreadId) {
        refreshHistory();
      }

    } catch (err) {
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: 'Failed to send message.' 
      }));
    }
  };

  const deleteThread = async (threadId: string) => {
    if (!userId) return;
    try {
      await axios.delete(`${API_BASE}/chat/history/${threadId}?user_id=${userId}`);
      if (state.currentThreadId === threadId) {
        createNewThread();
      }
      refreshHistory();
    } catch (err) {
      console.error(err);
    }
  };

  const setSelectedAgent = (id: number | null) => {
    setState(prev => ({ ...prev, selectedAgentId: id }));
  };

  return (
    <ChatContext.Provider value={{ 
      ...state, 
      sendMessage, 
      loadThread, 
      createNewThread, 
      deleteThread,
      refreshHistory,
      setSelectedAgent 
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error('useChat must be used within ChatProvider');
  return context;
};
