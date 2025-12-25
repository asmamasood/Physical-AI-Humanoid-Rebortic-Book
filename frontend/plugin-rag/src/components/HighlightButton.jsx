/**
 * HighlightButton Component.
 * 
 * Floating button that appears when text is selected,
 * allowing users to ask about the selection.
 */

import React from 'react';
import styles from './HighlightButton.module.css';

/**
 * Floating button for text selection queries.
 * 
 * @param {Object} props
 * @param {{top: number, left: number}} props.position - Button position
 * @param {Function} props.onClick - Click handler
 * @param {boolean} props.disabled - Whether button is disabled
 */
export default function HighlightButton({ position, onClick, disabled }) {
    return (
        <button
            data-highlight-button
            className={styles.highlightButton}
            style={{
                position: 'absolute',
                top: `${position.top}px`,
                left: `${position.left}px`,
                transform: 'translateX(-50%)',
            }}
            onClick={onClick}
            disabled={disabled}
            title="Ask about this selection"
        >
            💬 Ask about selection
        </button>
    );
}
