import React from 'react';
import { useHistory, useLocation } from '@docusaurus/router';
import { useSession } from '../lib/auth-client';
import useBaseUrl from '@docusaurus/useBaseUrl';
import FloatingChat from '../components/FloatingChat';
import ChatBoard from '../components/ChatBoard/ChatBoard';
import { ChatProvider } from '../components/ChatKit/ChatProvider';

// Default implementation of Root
export default function Root({ children }) {
  const { data: session, isPending } = useSession();
  const history = useHistory();
  const location = useLocation();
  
  // Get paths
  const loginPath = useBaseUrl('/login');
  const signupPath = useBaseUrl('/signup');
  const homePath = useBaseUrl('/');
  
  // Check if current path is a public path or the home page
  const normalize = (path: string) => path.endsWith('/') && path.length > 1 ? path.slice(0, -1) : path;
  const currentPath = normalize(location.pathname);

  const isPublicPath = currentPath === normalize(loginPath) || 
                       currentPath === normalize(signupPath) || 
                       currentPath === normalize(homePath) ||
                       currentPath.startsWith(normalize(homePath + 'blog'));
  
  const isBookPage = location.pathname.startsWith('/docs/');
  const isBlogPage = location.pathname.startsWith('/blog');

  // AUTH GUARD
  if (!isPending && !session && !isPublicPath) {
    if (typeof window !== 'undefined') {
       history.replace(loginPath);
       return null;
    }
  }

  return (
    <ChatProvider>
      {children}
      {/* Show the persistent ChatBoard on book and blog pages */}
      {(isBookPage || isBlogPage) && (
        <ChatBoard isInline={false} />
      )}
      {/* Show special FloatingChat for home page if logged in */}
      {session && !isBookPage && !isBlogPage && <FloatingChat />}
    </ChatProvider>
  );
}
