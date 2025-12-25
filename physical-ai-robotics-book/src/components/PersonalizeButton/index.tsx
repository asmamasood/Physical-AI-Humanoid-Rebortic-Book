import React, { useState } from 'react';
import { useSession } from '../../lib/auth-client';
import { scrapeArticle } from '../../lib/scraper';
import styles from './styles.module.css';
import ReactMarkdown from 'react-markdown';

interface PersonalizeButtonProps {
  chapterTitle?: string;
  chapterContent?: string;
}

export default function PersonalizeButton({ chapterTitle, chapterContent }: PersonalizeButtonProps) {
  const { data: session } = useSession();
  const [personalized, setPersonalized] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [profileSummary, setProfileSummary] = useState<string | null>(null);

  const handlePersonalize = async () => {
    if (!session?.user?.id) {
      alert('Please sign in to personalize content.');
      return;
    }

    // Auto-scrape content if not provided props
    let title = chapterTitle;
    let content = chapterContent;

    if (!content && typeof document !== 'undefined') {
       content = scrapeArticle(document.querySelector('article'));
    }
    if (!title && typeof document !== 'undefined') {
       title = document.querySelector('h1')?.innerText || 'Untitled Chapter';
    }

    if (!content) {
      alert('Could not find chapter content to personalize.');
      return;
    }


    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/personalize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: session.user.id,
          chapter_title: title,
          chapter_content: content
        })
      });

      const data = await response.json();
      if (data.personalization_applied) {
        setPersonalized(data.personalized_content);
        setProfileSummary(data.user_profile_summary);
      } else {
        alert(data.user_profile_summary || 'Could not personalize. Please complete your profile.');
      }
    } catch (err) {
      alert('Failed to personalize content.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setPersonalized(null);
    setProfileSummary(null);
  };

  if (!session) {
    return null;
  }

  return (
    <div className={styles.container}>
      {!personalized ? (
        <button
          className={styles.button}
          onClick={handlePersonalize}
          disabled={loading}
        >
          {loading ? '✨ Personalizing...' : '✨ Personalize this chapter'}
        </button>
      ) : (
        <div className={styles.personalizedBanner}>
          <span>📚 Personalized for: {profileSummary}</span>
          <button className={styles.resetButton} onClick={handleReset}>
            Show Original
          </button>
        </div>
      )}

      {personalized && (
        <div className={styles.personalizedContent}>
          <ReactMarkdown>{personalized}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}

