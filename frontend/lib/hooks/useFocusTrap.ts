import { useEffect, useRef } from 'react';

interface FocusTrapOptions {
  active?: boolean;
  initialFocus?: boolean;
  returnFocus?: boolean;
  escapeDeactivates?: boolean;
  onDeactivate?: () => void;
}

export function useFocusTrap({
  active = true,
  initialFocus = true,
  returnFocus = true,
  escapeDeactivates = true,
  onDeactivate,
}: FocusTrapOptions = {}) {
  const containerRef = useRef<HTMLElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!active || !containerRef.current) return;

    const container = containerRef.current;

    // Save the currently focused element
    previousActiveElement.current = document.activeElement as HTMLElement;

    // Get all focusable elements
    const getFocusableElements = () => {
      return Array.from(
        container.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
      ).filter((el) => !el.hasAttribute('disabled'));
    };

    // Set initial focus
    if (initialFocus) {
      const focusableElements = getFocusableElements();
      if (focusableElements.length > 0) {
        focusableElements[0].focus();
      }
    }

    // Handle tab key
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        const focusableElements = getFocusableElements();
        if (!focusableElements.length) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        const activeElement = document.activeElement;

        if (event.shiftKey) {
          // Shift + Tab
          if (activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          }
        } else {
          // Tab
          if (activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      } else if (event.key === 'Escape' && escapeDeactivates) {
        onDeactivate?.();
      }
    };

    // Handle focus outside container
    const handleFocusOutside = (event: FocusEvent) => {
      if (
        container &&
        !container.contains(event.target as Node) &&
        event.target !== container
      ) {
        event.preventDefault();
        const focusableElements = getFocusableElements();
        if (focusableElements.length > 0) {
          focusableElements[0].focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('focusin', handleFocusOutside);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('focusin', handleFocusOutside);

      // Return focus to the previously active element
      if (returnFocus && previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    };
  }, [active, initialFocus, returnFocus, escapeDeactivates, onDeactivate]);

  return containerRef;
}
