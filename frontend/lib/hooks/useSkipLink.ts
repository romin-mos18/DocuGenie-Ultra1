import { useEffect, useRef } from 'react';

interface SkipLinkOptions {
  mainContentId?: string;
  label?: string;
}

export function useSkipLink({
  mainContentId = 'main-content',
  label = 'Skip to main content',
}: SkipLinkOptions = {}) {
  const skipLinkRef = useRef<HTMLAnchorElement | null>(null);

  useEffect(() => {
    // Create skip link if it doesn't exist
    if (!skipLinkRef.current) {
      const skipLink = document.createElement('a');
      skipLink.href = `#${mainContentId}`;
      skipLink.textContent = label;
      skipLink.className = 'skip-link';
      skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 0;
        padding: 8px;
        background-color: #1976d2;
        color: white;
        z-index: 9999;
        transition: top 0.2s;
      `;

      // Show on focus
      skipLink.addEventListener('focus', () => {
        skipLink.style.top = '0';
      });

      // Hide on blur
      skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-40px';
      });

      // Add to document
      document.body.insertBefore(skipLink, document.body.firstChild);
      skipLinkRef.current = skipLink;
    }

    // Ensure main content has the correct ID and tabindex
    const mainContent = document.getElementById(mainContentId);
    if (mainContent) {
      mainContent.tabIndex = -1;
    }

    return () => {
      // Clean up on unmount
      skipLinkRef.current?.remove();
    };
  }, [mainContentId, label]);

  return skipLinkRef;
}
