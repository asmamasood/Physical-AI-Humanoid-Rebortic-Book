import React from 'react';
import { useSession, signOut } from '../../lib/auth-client';

export default function NavbarAuthButton() {
  const { data: session, isPending } = useSession();

  if (isPending) {
    return null;
  }

  if (session) {
    return (
      <button
        onClick={async () => {
          await signOut();
          window.location.href = '/'; 
        }}
        className="button button--outline button--sm"
        style={{
          marginLeft: '8px',
          border: '1px solid var(--ifm-color-primary)',
          color: 'var(--ifm-color-primary)',
          fontWeight: 600,
          borderRadius: '20px',
          padding: '4px 15px'
        }}
      >
        Sign Out
      </button>
    );
  }

  return null;
}
