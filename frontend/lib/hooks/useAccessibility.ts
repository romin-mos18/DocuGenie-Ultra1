import { useCallback, useEffect, useRef, useState } from 'react';
import { useFocusTrap, useLiveRegion, handleKeyboardNavigation, getAriaDescribedBy, getAriaInvalid } from '../accessibility';

export const useAccessibility = () => {
  const [isHighContrast, setIsHighContrast] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const announce = useLiveRegion();
  const focusTrapRef = useFocusTrap();
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // Detect high contrast mode
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    setIsHighContrast(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setIsHighContrast(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Detect reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Focus management
  const saveFocus = useCallback(() => {
    previousFocusRef.current = document.activeElement as HTMLElement;
  }, []);

  const restoreFocus = useCallback(() => {
    if (previousFocusRef.current) {
      previousFocusRef.current.focus();
    }
  }, []);

  const focusFirstInteractive = useCallback((container: HTMLElement) => {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    if (firstElement) {
      firstElement.focus();
    }
  }, []);

  // Announcement utilities
  const announceSuccess = useCallback((message: string) => {
    announce(message, 'polite');
  }, [announce]);

  const announceError = useCallback((message: string) => {
    announce(message, 'assertive');
  }, [announce]);

  const announceLoading = useCallback((message: string) => {
    announce(message, 'polite');
  }, [announce]);

  // Form accessibility helpers
  const getFormFieldAriaProps = useCallback((props: {
    name: string;
    error?: string;
    helperText?: string;
    'aria-label'?: string;
    'aria-describedby'?: string;
  }) => {
    const hasError = !!props.error;
    const errorId = hasError ? `${props.name}-error` : undefined;
    const helpId = props.helperText ? `${props.name}-help` : undefined;
    
    return {
      'aria-describedby': props['aria-describedby'] || getAriaDescribedBy(errorId, helpId),
      'aria-invalid': hasError ? true : false,
      'aria-label': props['aria-label'],
    };
  }, []);

  // Keyboard navigation handler
  const handleKeyDown = useCallback((
    event: React.KeyboardEvent,
    handlers: {
      onEnter?: () => void;
      onEscape?: () => void;
      onArrowUp?: () => void;
      onArrowDown?: () => void;
      onTab?: () => void;
    }
  ) => {
    handleKeyboardNavigation(
      event,
      handlers.onEnter,
      handlers.onEscape,
      handlers.onArrowUp,
      handlers.onArrowDown
    );
  }, []);

  // Accessibility state
  const accessibilityState = {
    isHighContrast,
    prefersReducedMotion,
  };

  return {
    // Focus management
    focusTrapRef,
    saveFocus,
    restoreFocus,
    focusFirstInteractive,
    
    // Announcements
    announceSuccess,
    announceError,
    announceLoading,
    
    // Form helpers
    getFormFieldAriaProps,
    
    // Keyboard navigation
    handleKeyDown,
    
    // State
    accessibilityState,
  };
};
