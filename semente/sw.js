// Semente Diária: recebe as notificações e abre o app ao tocar.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('push', e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (_) { d = { title: 'Semente Diária', body: e.data && e.data.text() }; }
  e.waitUntil(self.registration.showNotification(d.title || 'Semente Diária', {
    body: d.body || 'Sua semente de hoje chegou.',
    icon: 'icon-192.png', badge: 'icon-192.png', tag: d.tag || 'semente', renotify: true,
    data: { url: d.url || self.registration.scope }
  }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = (e.notification.data && e.notification.data.url) || self.registration.scope;
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => {
    for (const c of cs) if (c.url.startsWith(self.registration.scope)) return c.focus();
    return self.clients.openWindow(url);
  }));
});
