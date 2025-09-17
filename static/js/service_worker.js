// Minimal service worker for PWA install capability
// No caching - always fetch from network

self.addEventListener('install', event => {
  // Skip waiting to activate immediately
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  // Take control of all clients immediately
  event.waitUntil(self.clients.claim());
});

// Fetch event - pass everything through to network
self.addEventListener('fetch', event => {
  // Simply pass all requests through to the network
  // No caching, no offline handling
  event.respondWith(fetch(event.request));
});