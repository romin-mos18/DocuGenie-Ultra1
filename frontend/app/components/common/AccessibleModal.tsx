'use client';

import React, { useEffect, useRef } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Box } from '@mui/material';
import { useAccessibility } from '../../../lib/hooks/useAccessibility';

interface AccessibleModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  fullWidth?: boolean;
}

export default function AccessibleModal({
  open,
  onClose,
  title,
  children,
  actions,
  maxWidth = 'sm',
  fullWidth = false,
}: AccessibleModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const { focusTrapRef, saveFocus, restoreFocus, focusFirstInteractive, announceLoading } = useAccessibility();

  // Handle modal open/close
  useEffect(() => {
    if (open) {
      // Save current focus
      saveFocus();
      
      // Announce modal opening
      announceLoading(`${title} dialog opened`);
      
      // Focus first interactive element after a short delay
      setTimeout(() => {
        if (modalRef.current) {
          focusFirstInteractive(modalRef.current);
        }
      }, 100);
    } else {
      // Restore previous focus
      restoreFocus();
    }
  }, [open, title, saveFocus, restoreFocus, focusFirstInteractive, announceLoading]);

  // Handle escape key
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      onClose();
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={maxWidth}
      fullWidth={fullWidth}
      aria-labelledby="modal-title"
      aria-describedby="modal-description"
      role="dialog"
      aria-modal="true"
      ref={modalRef}
      onKeyDown={handleKeyDown}
      sx={{
        '& .MuiDialog-paper': {
          borderRadius: 2,
          boxShadow: 24,
        },
      }}
    >
      <Box ref={modalRef}>
        <DialogTitle
          id="modal-title"
          component="h2"
          sx={{
            fontWeight: 600,
            borderBottom: '1px solid',
            borderColor: 'divider',
            pb: 2,
          }}
        >
          {title}
        </DialogTitle>
        
        <DialogContent
          id="modal-description"
          sx={{
            pt: 2,
            pb: actions ? 1 : 2,
          }}
        >
          {children}
        </DialogContent>
        
        {actions && (
          <DialogActions
            sx={{
              px: 3,
              py: 2,
              borderTop: '1px solid',
              borderColor: 'divider',
            }}
          >
            {actions}
          </DialogActions>
        )}
      </Box>
    </Dialog>
  );
}
