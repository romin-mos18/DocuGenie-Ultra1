import { useState } from 'react'

export interface NotificationState {
  open: boolean
  message: string
  severity: 'success' | 'error' | 'warning' | 'info'
}

export const useNotification = () => {
  const [notification, setNotification] = useState<NotificationState>({
    open: false,
    message: '',
    severity: 'success'
  })

  const showNotification = (
    message: string, 
    severity: 'success' | 'error' | 'warning' | 'info' = 'success'
  ) => {
    setNotification({ open: true, message, severity })
  }

  const hideNotification = () => {
    setNotification({ ...notification, open: false })
  }

  const showSuccess = (message: string) => showNotification(message, 'success')
  const showError = (message: string) => showNotification(message, 'error')
  const showWarning = (message: string) => showNotification(message, 'warning')
  const showInfo = (message: string) => showNotification(message, 'info')

  return {
    notification,
    showNotification,
    hideNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
}
