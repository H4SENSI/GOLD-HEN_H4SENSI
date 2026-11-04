"use strict";

const CACHE_VERSION = "15";
const CACHE_NAME = "h4sensi-offline-v" + CACHE_VERSION;
const SHELL = [
  "./",
  "./index.html",
  "./cache.html",
  "./asset-manifest.json"
];

async function cacheRequest(cache, url) {
  try {
    const response = await fetch(url, { cache: "no-store" });
    if (!response || !response.ok || response.type === "opaque") return false;
    if (response.headers.get("content-length") === "0") return false;
    await cache.put(url, response.clone());
    return true;
  } catch (_) {
    return false;
  }
}

async function broadcast(message) {
  const clients = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
  for (const client of clients) client.postMessage(message);
}

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    // The shell is required. Do not activate a worker that cannot serve it.
    await cache.addAll(SHELL);
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys
      .filter((key) => key.startsWith("h4sensi-offline-") && key !== CACHE_NAME)
      .map((key) => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener("message", (event) => {
  const data = event.data;
  if (!data) return;

  if (data.type === "SKIP_WAITING") {
    event.waitUntil(self.skipWaiting());
    return;
  }

  if (data.type !== "CACHE_URLS" || !Array.isArray(data.urls)) return;

  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    const scope = new URL(self.registration.scope);
    const urls = [...new Set(data.urls.filter((value) => typeof value === "string"))];
    let done = 0;
    let ok = 0;
    let failed = 0;

    for (const value of urls) {
      let target;
      let saved = false;
      try {
        target = new URL(value, scope);
        const insideScope = target.pathname.startsWith(scope.pathname);
        if (target.origin === scope.origin && insideScope && target.protocol === scope.protocol) {
          saved = await cacheRequest(cache, target.href);
        }
      } catch (_) {
        saved = false;
      }

      if (saved) ok++;
      else failed++;
      done++;
      await broadcast({ type: "PRECACHE_PROGRESS", done, total: urls.length, ok, failed });
    }

    await broadcast({ type: "PRECACHE_DONE", done, total: urls.length, ok, failed });
  })());
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.endsWith("/sw.js")) return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);

    // Integrity scans ask for a fresh response first. When offline, fall back
    // to the cached copy so it can still be checked against the pinned manifest.
    if (request.cache === "reload") {
      try {
        const response = await fetch(request);
        if (response && response.ok && response.type !== "opaque") {
          await cache.put(request, response.clone());
        }
        return response;
      } catch (error) {
        const cached = await cache.match(request);
        if (cached) return cached;
        throw error;
      }
    }

    const cached = await cache.match(request);
    if (cached) return cached;

    try {
      const response = await fetch(request);
      if (response && response.ok && response.type !== "opaque") {
        await cache.put(request, response.clone()).catch(() => {});
      }
      return response;
    } catch (error) {
      if (request.mode === "navigate") {
        const shell = await cache.match("./index.html");
        if (shell) return shell;
      }
      throw error;
    }
  })());
});
