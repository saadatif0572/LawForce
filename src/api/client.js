/**
 * Centralized API Client for LAWVERSE
 * Handles authentication headers, error normalization, and SSE streaming.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchApi(endpoint, options = {}) {
  const token = localStorage.getItem('lawverse_auth_token') || 'dev_token';
  
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers,
  };

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errData.detail || `Request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Stream legal query response via Server-Sent Events (SSE)
 */
export async function streamLegalQuery({ query, chatId, jurisdiction, province, language, onToken, onDone, onError }) {
  const token = localStorage.getItem('lawverse_auth_token') || 'dev_token';
  const url = `${API_BASE}/api/v1/chat/query/stream`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        query,
        chat_id: chatId,
        jurisdiction: jurisdiction || 'all',
        province: province || null,
        language: language || 'en',
      }),
    });

    if (!response.ok) {
      throw new Error(`Streaming failed with status ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data: ')) {
          try {
            const payload = JSON.parse(trimmed.replace('data: ', ''));
            if (payload.event === 'token') {
              onToken && onToken(payload.data);
            } else if (payload.event === 'done') {
              onDone && onDone(payload.data);
            }
          } catch (e) {
            console.error('Error parsing SSE line:', trimmed, e);
          }
        }
      }
    }
  } catch (error) {
    console.error('Stream Query Error:', error);
    onError && onError(error);
  }
}
