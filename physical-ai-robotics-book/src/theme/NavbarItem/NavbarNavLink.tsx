import React from 'react';
import NavbarNavLink from '@theme-original/NavbarItem/NavbarNavLink';
import NavbarAuthButton from '@site/src/components/NavbarAuthButton';
import { useSession } from '@site/src/lib/auth-client';

export default function NavbarNavLinkWrapper(props) {
  const { data: session } = useSession();
  
  // Normalize path (remove trailing slash) to ensure reliable matching
  const path = props.to ? props.to.replace(/\/$/, '') : '';

  // If user is logged in
  if (session) {
    // Hide "Sign Up" completely
    if (path === '/signup') return null;

    // Replace "Sign In" with a "Profile" link (rendered as a normal nav link)
    // and let the NavbarAuthButton handle the Sign Out.
    if (path === '/login') {
      // In this specific implementation, we return the Auth button for /login
      // But we also want a /profile link.
      // Docusaurus Navbar items are handled individually. 
      // If we want TWO items, we might need a different strategy or just hack it here.
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
           <NavbarNavLink {...props} to="/profile" label="Profile" />
           <NavbarAuthButton />
        </div>
      );
    }
  } else {
    // If user is logged out, allow both Sign In and Sign Up to render normally
  }

  // Default rendering for other links or when logged out
  return (
    <>
      <NavbarNavLink {...props} />
    </>
  );
}
