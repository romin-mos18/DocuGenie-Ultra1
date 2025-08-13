const CACHE_NAME = 'docugenie-cache-v1';
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png',
];

const API_CACHE_NAME = 'docugenie-api-cache-v1';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8007';

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== API_CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
});

// Helper function to determine if a request is for an API endpoint
const isApiRequest = (request) => {
  return request.url.startsWith(API_BASE_URL);
};

// Helper function to determine if a request is for a static asset
const isStaticAsset = (request) => {
  return STATIC_ASSETS.some((asset) => request.url.endsWith(asset));
};

// Helper function to determine if a request is for an image
const isImageRequest = (request) => {
  return request.destination === 'image';
};

// Helper function to determine if a request is for a document
const isDocumentRequest = (request) => {
  return request.url.includes('/documents/') && request.method === 'GET';
};

// Helper function to determine if we should cache the response
const shouldCache = (response) => {
  // Only cache successful responses
  if (!response.ok) return false;

  // Don't cache responses with no-store cache control
  const cacheControl = response.headers.get('cache-control');
  if (cacheControl && cacheControl.includes('no-store')) return false;

  return true;
};

// Fetch event - handle offline support
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    (async () => {
      const cache = await caches.open(isApiRequest(event.request) ? API_CACHE_NAME : CACHE_NAME);

      try {
        // Try to fetch from network first
        const response = await fetch(event.request);

        // Cache the response if appropriate
        if (
          shouldCache(response) &&
          (isStaticAsset(event.request) ||
            isImageRequest(event.request) ||
            isDocumentRequest(event.request))
        ) {
          cache.put(event.request, response.clone());
        }

        return response;
      } catch (error) {
        // If network request fails, try to return from cache
        const cachedResponse = await cache.match(event.request);
        if (cachedResponse) {
          return cachedResponse;
        }

        // If the request is for an API endpoint, return a custom offline response
        if (isApiRequest(event.request)) {
          return new Response(
            JSON.stringify({
              error: 'You are offline',
              offline: true,
            }),
            {
              status: 503,
              headers: { 'Content-Type': 'application/json' },
            }
          );
        }

        // For other requests, return the offline page
        return cache.match('/offline.html');
      }
    })()
  );
});

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-documents') {
    event.waitUntil(syncDocuments());
  }
});

// Function to sync documents when back online
async function syncDocuments() {
  try {
    const cache = await caches.open('docugenie-sync-cache');
    const requests = await cache.keys();

    await Promise.all(
      requests.map(async (request) => {
        try {
          const response = await fetch(request);
          if (response.ok) {
            await cache.delete(request);
          }
        } catch (error) {
          console.error('Failed to sync request:', error);
        }
      })
    );
  } catch (error) {
    console.error('Failed to sync documents:', error);
  }
}

// Push notification support
self.addEventListener('push', (event) => {
  const data = event.data.json();

  const options = {
    body: data.body,
    icon: '/logo192.png',
    badge: '/badge.png',
    data: data.url,
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.notification.data) {
    event.waitUntil(
      clients.openWindow(event.notification.data)
    );
  }
});
