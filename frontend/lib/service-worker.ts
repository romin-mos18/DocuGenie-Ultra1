export function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', async () => {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('ServiceWorker registration successful:', registration);

        // Request notification permission
        if ('Notification' in window) {
          const permission = await Notification.requestPermission();
          console.log('Notification permission:', permission);
        }

        // Register for background sync
        if ('sync' in registration) {
          await (registration as any).sync.register('sync-documents');
        }
      } catch (error) {
        console.error('ServiceWorker registration failed:', error);
      }
    });
  }
}

export function unregisterServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((registration) => {
      registration.unregister();
    });
  }
}

export async function checkOfflineCapability(): Promise<boolean> {
  if (!('serviceWorker' in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.ready;
    const cache = await caches.open('docugenie-cache-v1');
    return !!registration && !!cache;
  } catch {
    return false;
  }
}

export async function clearCache() {
  if ('caches' in window) {
    const cacheNames = await caches.keys();
    await Promise.all(
      cacheNames.map((cacheName) => caches.delete(cacheName))
    );
  }
}

export async function syncData() {
  if ('serviceWorker' in navigator && 'sync' in navigator.serviceWorker) {
    const registration = await navigator.serviceWorker.ready;
    await (registration as any).sync.register('sync-documents');
    return true;
  }
  return false;
}

export function subscribeToNotifications(callback: (notification: any) => void) {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data.type === 'notification') {
        callback(event.data);
      }
    });
  }
}

export function isOnline(): boolean {
  return navigator.onLine;
}

export function addOnlineStatusListener(callback: (online: boolean) => void) {
  window.addEventListener('online', () => callback(true));
  window.addEventListener('offline', () => callback(false));
}

export function removeOnlineStatusListener(callback: (online: boolean) => void) {
  window.removeEventListener('online', () => callback(true));
  window.removeEventListener('offline', () => callback(false));
}
