import { useCallback, useEffect, useRef } from 'react';

interface AriaAnnounceOptions {
  politeness?: 'polite' | 'assertive';
  clearAfter?: number;
}

export function useAriaAnnounce(options: AriaAnnounceOptions = {}) {
  const { politeness = 'polite', clearAfter = 5000 } = options;
  const announceRef = useRef<HTMLDivElement | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const announce = useCallback((message: string) => {
    if (!announceRef.current) {
      // Create the live region if it doesn't exist
      const liveRegion = document.createElement('div');
      liveRegion.setAttribute('role', 'status');
      liveRegion.setAttribute('aria-live', politeness);
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.style.position = 'absolute';
      liveRegion.style.width = '1px';
      liveRegion.style.height = '1px';
      liveRegion.style.padding = '0';
      liveRegion.style.margin = '-1px';
      liveRegion.style.overflow = 'hidden';
      liveRegion.style.clip = 'rect(0, 0, 0, 0)';
      liveRegion.style.whiteSpace = 'nowrap';
      liveRegion.style.border = '0';
      document.body.appendChild(liveRegion);
      announceRef.current = liveRegion;
    }

    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Update the message
    announceRef.current.textContent = message;

    // Clear the message after the specified time
    if (clearAfter > 0) {
      timeoutRef.current = setTimeout(() => {
        if (announceRef.current) {
          announceRef.current.textContent = '';
        }
      }, clearAfter);
    }
  }, [politeness, clearAfter]);

  useEffect(() => {
    return () => {
      // Clean up on unmount
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (announceRef.current) {
        announceRef.current.remove();
      }
    };
  }, []);

  return announce;
}
