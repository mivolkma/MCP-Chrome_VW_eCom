// Inject into the page (via MCP evaluate_script) BEFORE clicking "Zum Leasingantrag".
// Purpose: capture DUC leasing response links (ENTRY_POINT / CONTINUE_IN_CHECKOUT)
// and make them available as window.__FSAG_ENTRY_URL.
//
// Security defaults:
// - Redacts query/fragment when printing/logging.
// - Set window.__FSAG_ENTRY_URL_FULL only if you explicitly enable full mode.
//
// Usage (MCP):
// 1) evaluate_script with this snippet
// 2) click CTA
// 3) evaluate_script: () => window.__FSAG_ENTRY_URL (or __FSAG_ENTRY_URL_FULL)

(() => {
  const state = (window.__BTO_TRACE_STATE ||= {});

  const redactUrl = (url) => {
    if (typeof url !== 'string') return url;
    const q = url.indexOf('?');
    const h = url.indexOf('#');
    const cut = [q, h].filter((i) => i >= 0);
    const end = cut.length ? Math.min(...cut) : -1;
    return end >= 0 ? url.slice(0, end) : url;
  };

  const pickEntryUrl = (json) => {
    // Common shapes seen:
    // - { links: { ENTRY_POINT: { href }, CONTINUE_IN_CHECKOUT: { href } } }
    // - { _links: { ... } }
    // - array-ish or nested objects
    const candidates = [];

    const tryLinks = (linksObj) => {
      if (!linksObj || typeof linksObj !== 'object') return;
      for (const [k, v] of Object.entries(linksObj)) {
        const key = String(k || '').toUpperCase();
        const href = v && typeof v === 'object' ? (v.href || v.url) : undefined;
        if (typeof href === 'string') {
          candidates.push({ key, href });
        }
      }
    };

    tryLinks(json?.links);
    tryLinks(json?._links);

    // Fallback: deep search for strings that look like URLs
    const walk = (obj) => {
      if (!obj) return;
      if (typeof obj === 'string') {
        if (obj.startsWith('http://') || obj.startsWith('https://')) {
          candidates.push({ key: 'URL', href: obj });
        }
        return;
      }
      if (Array.isArray(obj)) {
        for (const v of obj) walk(v);
        return;
      }
      if (typeof obj === 'object') {
        for (const v of Object.values(obj)) walk(v);
      }
    };
    walk(json);

    // Prefer explicit keys
    const preferred = candidates.find((c) => c.key.includes('ENTRY_POINT'))
      || candidates.find((c) => c.key.includes('CONTINUE_IN_CHECKOUT'))
      || candidates[0];

    return preferred?.href;
  };

  const handleDucJson = (json, source) => {
    const url = pickEntryUrl(json);
    if (!url) return;

    state.lastDucSource = source;
    state.lastDucUrlRedacted = redactUrl(url);
    state.lastDucUrlFull = url;

    // Publish on window for later retrieval
    window.__FSAG_ENTRY_URL = state.lastDucUrlRedacted;
    // Only set full if explicitly enabled
    if (state.enableFullUrl === true) {
      window.__FSAG_ENTRY_URL_FULL = state.lastDucUrlFull;
    }

    // Minimal console output
    console.info('[BTO] DUC entry URL captured:', window.__FSAG_ENTRY_URL);
  };

  // Allow enabling full URL explicitly
  window.__BTO_ENABLE_FULL_FSAG_URL = () => {
    state.enableFullUrl = true;
    console.warn('[BTO] Full FSAG URL capture enabled (do not commit/log)');
  };

  // Patch fetch
  if (!state.fetchPatched) {
    const originalFetch = window.fetch.bind(window);
    window.fetch = async (...args) => {
      const res = await originalFetch(...args);
      try {
        const url = typeof args[0] === 'string' ? args[0] : args[0]?.url;
        if (typeof url === 'string' && url.includes('/bff/duc-leasing')) {
          const clone = res.clone();
          const ct = clone.headers.get('content-type') || '';
          if (ct.includes('application/json')) {
            const json = await clone.json();
            handleDucJson(json, 'fetch');
          }
        }
      } catch (_e) {
        // ignore
      }
      return res;
    };
    state.fetchPatched = true;
  }

  // Patch XHR
  if (!state.xhrPatched) {
    const XHR = window.XMLHttpRequest;
    const origOpen = XHR.prototype.open;
    const origSend = XHR.prototype.send;

    XHR.prototype.open = function (method, url, ...rest) {
      this.__bto_url = url;
      return origOpen.call(this, method, url, ...rest);
    };

    XHR.prototype.send = function (body) {
      try {
        this.addEventListener('load', function () {
          try {
            const url = this.__bto_url;
            if (typeof url === 'string' && url.includes('/bff/duc-leasing')) {
              const text = this.responseText;
              if (typeof text === 'string' && text.trim().startsWith('{')) {
                handleDucJson(JSON.parse(text), 'xhr');
              }
            }
          } catch (_e) {
            // ignore
          }
        });
      } catch (_e) {
        // ignore
      }
      return origSend.call(this, body);
    };

    state.xhrPatched = true;
  }

  console.info('[BTO] DUC entry tracer installed.');
})();
