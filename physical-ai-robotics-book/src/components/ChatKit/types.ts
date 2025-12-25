export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    agent_name?: string;
    created_at?: string;
}

export interface Thread {
    id: string;
    title: string;
    created_at: string;
}

export interface Agent {
    id: number;
    name: string;
    persona_description: string;
    skill_ids: number[];
}

export interface ChatState {
    messages: Message[];
    isLoading: boolean;
    error: string | null;
    currentThreadId: string | null;
    history: Thread[];
    agents: Agent[];
    selectedAgentId: number | null;
}

export interface ChatContextType extends ChatState {
    sendMessage: (content: string) => Promise<void>;
    loadThread: (threadId: string) => Promise<void>;
    createNewThread: () => void;
    deleteThread: (threadId: string) => Promise<void>;
    refreshHistory: () => Promise<void>;
    setSelectedAgent: (id: number | null) => void;
}
