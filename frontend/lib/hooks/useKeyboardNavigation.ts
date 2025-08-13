import { useEffect, useRef, useState } from 'react';

interface KeyboardNavigationOptions {
  itemSelector: string;
  onSelect?: (element: HTMLElement) => void;
  onEscape?: () => void;
  loop?: boolean;
  vertical?: boolean;
  horizontal?: boolean;
  grid?: boolean;
  gridColumns?: number;
}

export function useKeyboardNavigation({
  itemSelector,
  onSelect,
  onEscape,
  loop = true,
  vertical = true,
  horizontal = false,
  grid = false,
  gridColumns = 1,
}: KeyboardNavigationOptions) {
  const containerRef = useRef<HTMLElement>(null);
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const items = Array.from(container.querySelectorAll<HTMLElement>(itemSelector));
    if (!items.length) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      let newIndex = focusedIndex;

      switch (event.key) {
        case 'ArrowUp':
          if (vertical || grid) {
            event.preventDefault();
            newIndex = grid
              ? Math.max(0, focusedIndex - gridColumns)
              : focusedIndex - 1;
          }
          break;

        case 'ArrowDown':
          if (vertical || grid) {
            event.preventDefault();
            newIndex = grid
              ? Math.min(items.length - 1, focusedIndex + gridColumns)
              : focusedIndex + 1;
          }
          break;

        case 'ArrowLeft':
          if (horizontal || grid) {
            event.preventDefault();
            newIndex = focusedIndex - 1;
          }
          break;

        case 'ArrowRight':
          if (horizontal || grid) {
            event.preventDefault();
            newIndex = focusedIndex + 1;
          }
          break;

        case 'Home':
          event.preventDefault();
          newIndex = 0;
          break;

        case 'End':
          event.preventDefault();
          newIndex = items.length - 1;
          break;

        case 'Enter':
        case ' ':
          event.preventDefault();
          if (focusedIndex >= 0 && focusedIndex < items.length) {
            onSelect?.(items[focusedIndex]);
          }
          return;

        case 'Escape':
          event.preventDefault();
          onEscape?.();
          return;

        default:
          return;
      }

      // Handle loop and bounds
      if (loop) {
        if (newIndex < 0) {
          newIndex = items.length - 1;
        } else if (newIndex >= items.length) {
          newIndex = 0;
        }
      } else {
        newIndex = Math.max(0, Math.min(items.length - 1, newIndex));
      }

      // Update focus
      if (newIndex !== focusedIndex && newIndex >= 0 && newIndex < items.length) {
        setFocusedIndex(newIndex);
        items[newIndex].focus();
      }
    };

    // Handle focus within container
    const handleFocus = (event: FocusEvent) => {
      const target = event.target as HTMLElement;
      const index = items.indexOf(target);
      if (index !== -1) {
        setFocusedIndex(index);
      }
    };

    // Handle blur outside container
    const handleBlur = (event: FocusEvent) => {
      const relatedTarget = event.relatedTarget as HTMLElement;
      if (!container.contains(relatedTarget)) {
        setFocusedIndex(-1);
      }
    };

    container.addEventListener('keydown', handleKeyDown);
    container.addEventListener('focus', handleFocus, true);
    container.addEventListener('blur', handleBlur, true);

    return () => {
      container.removeEventListener('keydown', handleKeyDown);
      container.removeEventListener('focus', handleFocus, true);
      container.removeEventListener('blur', handleBlur, true);
    };
  }, [
    itemSelector,
    onSelect,
    onEscape,
    loop,
    vertical,
    horizontal,
    grid,
    gridColumns,
    focusedIndex,
  ]);

  return {
    containerRef,
    focusedIndex,
  };
}
