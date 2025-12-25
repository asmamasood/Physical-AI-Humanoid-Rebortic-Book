import React, { useState } from 'react';
import { useSession } from '../../lib/auth-client';
import { scrapeArticle } from '../../lib/scraper';
import styles from './styles.module.css';

interface TranslateButtonProps {
    content?: string;
    onTranslate?: (translated: string | null) => void;
}

export default function TranslateButton({ content, onTranslate }: TranslateButtonProps) {
    const { data: session } = useSession();
    const [isUrdu, setIsUrdu] = useState(false);
    const [loading, setLoading] = useState(false);
    const [originalContent, setOriginalContent] = useState<string | null>(null);
    const [urduContent, setUrduContent] = useState<string | null>(null);

    const handleTranslate = async () => {
        const newIsUrdu = !isUrdu;
        
        if (!newIsUrdu) {
            setIsUrdu(false);
            if (onTranslate) onTranslate(null);
            // Save preference
            if (session?.user?.id) {
                savePreference('en');
            }
            return;
        }

        if (urduContent) {
            setIsUrdu(true);
            if (onTranslate) onTranslate(urduContent);
            if (session?.user?.id) {
                savePreference('ur');
            }
            return;
        }

        let textToTranslate = content;
        if (!textToTranslate && typeof document !== 'undefined') {
            textToTranslate = scrapeArticle(document.querySelector('article'));
        }

        if (!textToTranslate) {
            alert('No content found to translate.');
            return;
        }


        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: textToTranslate })
            });

            const data = await response.json();
            if (data.translated_text) {
                setUrduContent(data.translated_text);
                setIsUrdu(true);
                if (onTranslate) onTranslate(data.translated_text);
                if (session?.user?.id) {
                    savePreference('ur');
                }
            }
        } catch (err) {
            alert('Translation failed.');
        } finally {
            setLoading(false);
        }
    };

    const savePreference = async (lang: string) => {
        if (!session?.user?.id) return;
        
        try {
            // First get existing profile to avoid overwriting background info
            const profileRes = await fetch(`http://localhost:8000/api/profile/${session.user.id}`);
            const profile = await profileRes.json();
            
            await fetch('http://localhost:8000/api/profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: session.user.id,
                    software_role: profile.software_role || 'General',
                    software_level: profile.software_level || 'Intermediate',
                    hardware_type: profile.hardware_type || 'Mid-range PC',
                    gpu_available: profile.gpu_available || false,
                    preferred_language: lang
                })
            });
        } catch (err) {
            console.error('Failed to save language preference:', err);
        }
    };

    if (!session) return null;

    return (
        <button 
            className={`${styles.button} ${isUrdu ? styles.active : ''}`}
            onClick={handleTranslate}
            disabled={loading}
        >
            {loading ? '⏳ Translating...' : isUrdu ? '🇺🇳 Show English' : '🇵🇰 Translate to Urdu'}
        </button>
    );
}
