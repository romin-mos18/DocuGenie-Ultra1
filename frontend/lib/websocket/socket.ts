import { io, Socket } from 'socket.io-client';
import { store } from '../../app/store/store';
import { addDocument, updateDocument } from '../../app/store/slices/documentSlice';
import { addNotification } from '../../app/store/slices/uiSlice';

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second

  constructor() {
    this.initializeSocket();
  }

  private initializeSocket() {
    // Check if we're in a browser environment
    if (typeof window === 'undefined') return;
    
    const token = localStorage.getItem('token');
    if (!token) return;

    this.socket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8007', {
      auth: {
        token,
      },
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    });

    this.setupEventListeners();
  }

  private setupEventListeners() {
    if (!this.socket) return;

    // Connection events
    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
    });

    this.socket.on('disconnect', (reason: string) => {
      console.log('WebSocket disconnected:', reason);
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, try to reconnect
        this.reconnect();
      }
    });

    this.socket.on('connect_error', (error: Error) => {
      console.error('WebSocket connection error:', error);
      this.handleReconnect();
    });

    // Document events
    this.socket.on('document:created', (document: any) => {
      store.dispatch(addDocument(document));
      store.dispatch(
        addNotification({
          id: Date.now().toString(),
          type: 'info',
          message: 'New document uploaded',
        })
      );
    });

    this.socket.on('document:updated', (document: any) => {
      store.dispatch(updateDocument(document));
      store.dispatch(
        addNotification({
          id: Date.now().toString(),
          type: 'info',
          message: `Document "${document.title}" updated`,
        })
      );
    });

    this.socket.on('document:processing', ({ documentId, status, progress }: { documentId: string; status: string; progress: number }) => {
      store.dispatch(
        updateDocument({
          id: documentId,
          status,
          processingProgress: progress,
        } as any)
      );
    });

    this.socket.on('document:processed', (document: any) => {
      store.dispatch(updateDocument(document));
      store.dispatch(
        addNotification({
          id: Date.now().toString(),
          type: 'success',
          message: `Document "${document.title}" processed successfully`,
        })
      );
    });

    this.socket.on('document:error', ({ documentId, error }: { documentId: string; error: string }) => {
      store.dispatch(
        updateDocument({
          id: documentId,
          status: 'error',
          error,
        } as any)
      );
      store.dispatch(
        addNotification({
          id: Date.now().toString(),
          type: 'error',
          message: `Error processing document: ${error}`,
        })
      );
    });

    // System events
    this.socket.on('system:maintenance', (message: string) => {
      store.dispatch(
        addNotification({
          id: Date.now().toString(),
          type: 'warning',
          message,
          autoHideDuration: undefined, // Don't auto-hide maintenance notifications
        })
      );
    });

    this.socket.on('system:error', (message: string) => {
      store.dispatch(
        addNotification({
          id: Date.now().toString(),
          type: 'error',
          message,
        })
      );
    });
  }

  private handleReconnect() {
    this.reconnectAttempts++;
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      // Exponential backoff
      this.reconnectDelay *= 2;
      setTimeout(() => this.reconnect(), this.reconnectDelay);
    } else {
      store.dispatch(
        addNotification({
          id: Date.now().toString(),
          type: 'error',
          message: 'Failed to connect to server. Please refresh the page.',
          autoHideDuration: undefined,
        })
      );
    }
  }

  private reconnect() {
    if (this.socket) {
      this.socket.connect();
    } else {
      this.initializeSocket();
    }
  }

  public connect() {
    if (!this.socket) {
      this.initializeSocket();
    } else if (!this.socket.connected) {
      this.socket.connect();
    }
  }

  public disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  public isConnected(): boolean {
    return !!this.socket?.connected;
  }

  public emit(event: string, data: any) {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('WebSocket not connected. Message not sent:', event, data);
    }
  }

  public subscribe(event: string, callback: (data: any) => void) {
    this.socket?.on(event, callback);
  }

  public unsubscribe(event: string, callback: (data: any) => void) {
    this.socket?.off(event, callback);
  }
}

// Create a singleton instance
const socketService = new WebSocketService();

export default socketService;
