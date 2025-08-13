import React, { createContext, useContext, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../../app/store/store';
import { useWebSocket } from './useWebSocket';
import { addNotification } from '../../app/store/slices/uiSlice';

interface WebSocketContextValue {
  isConnected: () => boolean;
  emit: (event: string, data: any) => void;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

export function useWebSocketContext() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
}

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

  const { emit, isConnected } = useWebSocket(
    [], // Base subscriptions are handled in the socket service
    {
      onConnect: () => {
        dispatch(
          addNotification({
            id: Date.now().toString(),
            type: 'success',
            message: 'Connected to server',
            autoHideDuration: 3000,
          })
        );
      },
      onDisconnect: () => {
        dispatch(
          addNotification({
            id: Date.now().toString(),
            type: 'warning',
            message: 'Disconnected from server. Attempting to reconnect...',
          })
        );
      },
      onError: (error) => {
        dispatch(
          addNotification({
            id: Date.now().toString(),
            type: 'error',
            message: `Connection error: ${error.message}`,
          })
        );
      },
    }
  );

  // Only provide WebSocket context when authenticated
  const value = isAuthenticated ? { emit, isConnected } : null;

  return (
    <WebSocketContext.Provider value={value}>{children}</WebSocketContext.Provider>
  );
}
