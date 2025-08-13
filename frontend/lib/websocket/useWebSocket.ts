import { useEffect, useCallback } from 'react';
import socketService from './socket';

interface UseWebSocketOptions {
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

interface UseWebSocketSubscription {
  event: string;
  callback: (data: any) => void;
}

export function useWebSocket(
  subscriptions: UseWebSocketSubscription[] = [],
  options: UseWebSocketOptions = {}
) {
  const { onConnect, onDisconnect, onError } = options;

  useEffect(() => {
    // Connect to WebSocket
    socketService.connect();

    // Setup event listeners
    if (onConnect) {
      socketService.subscribe('connect', onConnect);
    }
    if (onDisconnect) {
      socketService.subscribe('disconnect', onDisconnect);
    }
    if (onError) {
      socketService.subscribe('connect_error', onError);
    }

    // Setup subscriptions
    subscriptions.forEach(({ event, callback }) => {
      socketService.subscribe(event, callback);
    });

    // Cleanup
    return () => {
      if (onConnect) {
        socketService.unsubscribe('connect', onConnect);
      }
      if (onDisconnect) {
        socketService.unsubscribe('disconnect', onDisconnect);
      }
      if (onError) {
        socketService.unsubscribe('connect_error', onError);
      }

      subscriptions.forEach(({ event, callback }) => {
        socketService.unsubscribe(event, callback);
      });
    };
  }, [subscriptions, onConnect, onDisconnect, onError]);

  const emit = useCallback((event: string, data: any) => {
    socketService.emit(event, data);
  }, []);

  const isConnected = useCallback(() => {
    return socketService.isConnected();
  }, []);

  return {
    emit,
    isConnected,
  };
}
