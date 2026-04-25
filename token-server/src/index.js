/**
 * GHL Token Server — Cloudflare Worker
 *
 * Manages Firebase JWT tokens for the GoHighLevel internal API.
 * Auto-refreshes tokens via Google's securetoken endpoint and
 * caches them in KV with a 50-minute TTL.
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS_HEADERS },
  });
}

function checkPin(url, env) {
  const pin = url.searchParams.get('pin');
  if (!pin || pin !== env.ADMIN_PIN) {
    return json({ error: 'invalid pin' }, 401);
  }
  return null;
}

// ─── Token refresh ──────────────────────────────────────────────

async function refreshFirebaseToken(refreshToken, apiKey) {
  const res = await fetch(
    `https://securetoken.googleapis.com/v1/token?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: refreshToken,
      }),
    },
  );

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Firebase refresh failed (${res.status}): ${body}`);
  }

  const data = await res.json();
  return {
    id_token: data.id_token,
    refresh_token: data.refresh_token,
    expires_in: Number(data.expires_in) || 3600,
  };
}

// ─── Route handlers ─────────────────────────────────────────────

async function handleGetToken(url, env) {
  const authErr = checkPin(url, env);
  if (authErr) return authErr;

  // Check for cached token
  const cached = await env.TOKEN_STORE.get('firebase_id_token', { type: 'json' });
  if (cached) {
    const age = Date.now() - cached.stored_at;
    const fiftyMinutes = 50 * 60 * 1000;
    if (age < fiftyMinutes) {
      const remaining = Math.floor((fiftyMinutes - age) / 1000);
      return json({ token: cached.token, expires_in: remaining });
    }
  }

  // Refresh
  const refreshToken = await env.TOKEN_STORE.get('firebase_refresh_token');
  if (!refreshToken) {
    return json({ error: 'no refresh token configured — POST /setup first' }, 400);
  }

  const result = await refreshFirebaseToken(refreshToken, env.FIREBASE_API_KEY);

  // Cache the new ID token (KV TTL = 55 min as safety margin)
  await env.TOKEN_STORE.put(
    'firebase_id_token',
    JSON.stringify({ token: result.id_token, stored_at: Date.now() }),
    { expirationTtl: 55 * 60 },
  );

  // If Google rotated the refresh token, store the new one
  if (result.refresh_token && result.refresh_token !== refreshToken) {
    await env.TOKEN_STORE.put('firebase_refresh_token', result.refresh_token);
  }

  return json({ token: result.id_token, expires_in: result.expires_in });
}

async function handleSetup(request, url, env) {
  const authErr = checkPin(url, env);
  if (authErr) return authErr;

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'invalid JSON body' }, 400);
  }

  if (!body.refresh_token) {
    return json({ error: 'refresh_token is required' }, 400);
  }

  const storable = {
    firebase_refresh_token: body.refresh_token,
    location_id: body.location_id,
    company_id: body.company_id,
    user_id: body.user_id,
  };

  const stored = [];
  for (const [key, value] of Object.entries(storable)) {
    if (value) {
      await env.TOKEN_STORE.put(key, value);
      stored.push(key);
    }
  }

  // Clear any cached ID token so the next /cli/token call uses the new refresh token
  await env.TOKEN_STORE.delete('firebase_id_token');

  return json({ ok: true, stored });
}

async function handleConfig(url, env) {
  const authErr = checkPin(url, env);
  if (authErr) return authErr;

  const refreshToken = await env.TOKEN_STORE.get('firebase_refresh_token');
  const locationId = await env.TOKEN_STORE.get('location_id');
  const companyId = await env.TOKEN_STORE.get('company_id');
  const userId = await env.TOKEN_STORE.get('user_id');

  const config = {
    has_refresh_token: !!refreshToken,
  };
  if (locationId) config.location_id = locationId;
  if (companyId) config.company_id = companyId;
  if (userId) config.user_id = userId;

  return json(config);
}

function handleHealth() {
  return json({ status: 'ok', service: 'ghl-token-server' });
}

// ─── Main fetch handler ─────────────────────────────────────────

export default {
  async fetch(request, env) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    const { pathname } = url;

    if (pathname === '/health' && request.method === 'GET') {
      return handleHealth();
    }

    if (pathname === '/cli/token' && request.method === 'GET') {
      return handleGetToken(url, env);
    }

    if (pathname === '/setup' && request.method === 'POST') {
      return handleSetup(request, url, env);
    }

    if (pathname === '/config' && request.method === 'GET') {
      return handleConfig(url, env);
    }

    return json({ error: 'not found' }, 404);
  },
};
