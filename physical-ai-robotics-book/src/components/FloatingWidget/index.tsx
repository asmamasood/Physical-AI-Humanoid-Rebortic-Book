
import React from 'react';
import styles from './styles.module.css';
import Link from '@docusaurus/Link';

function FloatingWidget() {
  if (typeof window !== 'undefined' && window.location.pathname === '/') {
    return null;
  }

  return (
    <div className={styles.floatingWidget}>
      <Link to="/chat" className={styles.widgetButton}>
        Chat
      </Link>
    </div>
  );
}

export default FloatingWidget;
