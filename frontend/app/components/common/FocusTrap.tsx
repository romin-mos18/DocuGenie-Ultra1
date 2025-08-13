'use client';

import React, { ReactNode } from 'react';
import { Box } from '@mui/material';
import { useFocusTrap } from '../../../lib/accessibility';

interface FocusTrapProps {
  children: ReactNode;
  isActive?: boolean;
  onEscape?: () => void;
}

export default function FocusTrap({ children, isActive = true, onEscape }: FocusTrapProps) {
  const containerRef = useFocusTrap(isActive);

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape' && onEscape) {
      event.preventDefault();
      onEscape();
    }
  };

  return (
    <Box
      ref={containerRef}
      onKeyDown={handleKeyDown}
      tabIndex={-1}
      role="dialog"
      aria-modal="true"
    >
      {children}
    </Box>
  );
}
