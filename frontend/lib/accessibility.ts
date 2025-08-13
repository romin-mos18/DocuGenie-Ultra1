import { useRef, useEffect, useCallback } from 'react';
import { useState } from 'react';

// Focus management utilities
export const useFocusTrap = (isActive: boolean = true) => {
  const containerRef = useRef<HTMLElement>(null);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!isActive || !containerRef.current) return;

    const focusableElements = containerRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    if (event.key === 'Tab') {
      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    }
  }, [isActive]);

  useEffect(() => {
    if (isActive) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isActive, handleKeyDown]);

  return containerRef;
};

// Skip link utility
export const useSkipLink = () => {
  const skipLinkRef = useRef<HTMLAnchorElement>(null);

  const focusMainContent = () => {
    const mainContent = document.querySelector('main');
    if (mainContent) {
      (mainContent as HTMLElement).focus();
    }
  };

  useEffect(() => {
    const skipLink = skipLinkRef.current;
    if (skipLink) {
      skipLink.addEventListener('click', focusMainContent);
      return () => skipLink.removeEventListener('click', focusMainContent);
    }
  }, []);

  return skipLinkRef;
};

// Live region announcements
export const useLiveRegion = () => {
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const liveRegion = document.getElementById('live-region') || createLiveRegion();
    liveRegion.setAttribute('aria-live', priority);
    liveRegion.textContent = message;
    
    // Clear the message after a short delay
    setTimeout(() => {
      liveRegion.textContent = '';
    }, 1000);
  }, []);

  return announce;
};

const createLiveRegion = () => {
  const liveRegion = document.createElement('div');
  liveRegion.id = 'live-region';
  liveRegion.setAttribute('aria-live', 'polite');
  liveRegion.setAttribute('aria-atomic', 'true');
  liveRegion.style.position = 'absolute';
  liveRegion.style.left = '-10000px';
  liveRegion.style.width = '1px';
  liveRegion.style.height = '1px';
  liveRegion.style.overflow = 'hidden';
  document.body.appendChild(liveRegion);
  return liveRegion;
};

// Keyboard navigation utilities
export const handleKeyboardNavigation = (
  event: React.KeyboardEvent,
  onEnter?: () => void,
  onEscape?: () => void,
  onArrowUp?: () => void,
  onArrowDown?: () => void
) => {
  switch (event.key) {
    case 'Enter':
    case ' ':
      event.preventDefault();
      onEnter?.();
      break;
    case 'Escape':
      event.preventDefault();
      onEscape?.();
      break;
    case 'ArrowUp':
      event.preventDefault();
      onArrowUp?.();
      break;
    case 'ArrowDown':
      event.preventDefault();
      onArrowDown?.();
      break;
  }
};

// ARIA helpers
export const getAriaDescribedBy = (errorId?: string, helpId?: string) => {
  const ids = [errorId, helpId].filter(Boolean);
  return ids.length > 0 ? ids.join(' ') : undefined;
};

export const getAriaInvalid = (hasError: boolean) => {
  return hasError ? 'true' : undefined;
};

// Color contrast utilities
export const getContrastRatio = (color1: string, color2: string): number => {
  const getLuminance = (color: string): number => {
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16) / 255;
    const g = parseInt(hex.substr(2, 2), 16) / 255;
    const b = parseInt(hex.substr(4, 2), 16) / 255;
    
    const [rs, gs, bs] = [r, g, b].map(c => {
      if (c <= 0.03928) return c / 12.92;
      return Math.pow((c + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };

  const luminance1 = getLuminance(color1);
  const luminance2 = getLuminance(color2);
  
  const brightest = Math.max(luminance1, luminance2);
  const darkest = Math.min(luminance1, luminance2);
  
  return (brightest + 0.05) / (darkest + 0.05);
};

export const isAccessibleContrast = (color1: string, color2: string): boolean => {
  const ratio = getContrastRatio(color1, color2);
  return ratio >= 4.5; // WCAG AA standard for normal text
};

// Screen reader utilities
export const announceToScreenReader = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
  const announce = useLiveRegion();
  announce(message, priority);
};

// Focus restoration
export const useFocusRestoration = () => {
  const previousFocusRef = useRef<HTMLElement | null>(null);

  const saveFocus = useCallback(() => {
    previousFocusRef.current = document.activeElement as HTMLElement;
  }, []);

  const restoreFocus = useCallback(() => {
    if (previousFocusRef.current) {
      previousFocusRef.current.focus();
    }
  }, []);

  return { saveFocus, restoreFocus };
};

// High contrast mode detection
export const useHighContrastMode = () => {
  const [isHighContrast, setIsHighContrast] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    setIsHighContrast(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setIsHighContrast(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return isHighContrast;
};

// Reduced motion detection
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
};
