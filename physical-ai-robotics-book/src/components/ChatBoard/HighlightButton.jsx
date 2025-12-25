import React from 'react';
import styles from './HighlightButton.module.css';

export default function HighlightButton({ position, onClick, disabled }) {
    return (
        <button
            data-highlight-button
            className={styles.highlightButton}
            style={{
                position: 'fixed',
                top: `${position.top}px`,
                left: `${position.left}px`,
                transform: 'translateX(-50%)',
                zIndex: 10001, // Higher than chatWindow to be clickable
            }}
            onClick={onClick}
            disabled={disabled}
            title="Ask about this selection"
        >
            💬 Ask about selection
        </button>
    );
}
