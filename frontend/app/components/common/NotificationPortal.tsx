'use client'

import React from 'react'
import { Snackbar, Alert } from '@mui/material'
import { NotificationState } from '../../../lib/hooks/useNotification'

interface NotificationPortalProps {
  notification: NotificationState
  onClose: () => void
}

export default function NotificationPortal({ notification, onClose }: NotificationPortalProps) {
  return (
    <Snackbar
      open={notification.open}
      autoHideDuration={6000}
      onClose={onClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
    >
      <Alert 
        onClose={onClose} 
        severity={notification.severity}
        sx={{
          backgroundColor: 'white',
          color: '#1f2937',
          border: `1px solid ${
            notification.severity === 'success' ? '#10b981' :
            notification.severity === 'error' ? '#ef4444' :
            notification.severity === 'warning' ? '#f59e0b' :
            '#3b82f6'
          }`,
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          minWidth: '300px',
          '& .MuiAlert-icon': {
            color: notification.severity === 'success' ? '#10b981' :
                   notification.severity === 'error' ? '#ef4444' :
                   notification.severity === 'warning' ? '#f59e0b' :
                   '#3b82f6'
          },
          '& .MuiAlert-message': {
            fontWeight: 500
          }
        }}
      >
        {notification.message}
      </Alert>
    </Snackbar>
  )
}
