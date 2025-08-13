'use client';

import React, { useState } from 'react';
import { Tooltip, Box } from '@mui/material';
import { useAccessibility } from '../../../lib/hooks/useAccessibility';

interface AccessibleTooltipProps {
  children: React.ReactNode;
  title: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
  arrow?: boolean;
  enterDelay?: number;
  leaveDelay?: number;
  'aria-label'?: string;
}

export default function AccessibleTooltip({
  children,
  title,
  placement = 'top',
  arrow = false,
  enterDelay = 200,
  leaveDelay = 0,
  'aria-label': ariaLabel,
}: AccessibleTooltipProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { announceLoading } = useAccessibility();

  const handleOpen = () => {
    setIsOpen(true);
    announceLoading(title);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  return (
    <Tooltip
      title={title}
      placement={placement}
      arrow={arrow}
      enterDelay={enterDelay}
      leaveDelay={leaveDelay}
      open={isOpen}
      onOpen={handleOpen}
      onClose={handleClose}
      PopperProps={{
        'aria-label': ariaLabel || title,
        role: 'tooltip',
        'aria-live': 'polite',
      }}
    >
      <Box
        component="span"
        onMouseEnter={handleOpen}
        onMouseLeave={handleClose}
        onFocus={handleOpen}
        onBlur={handleClose}
        tabIndex={0}
        role="button"
        aria-describedby={isOpen ? 'tooltip' : undefined}
      >
        {children}
      </Box>
    </Tooltip>
  );
}
