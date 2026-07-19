import { API_BASE_URL } from "@/config";

let isRefreshing = false;
let failedQueue: any[] = [];
let memoryAccessToken: string | null = null;

export function setAccessTokenInMemory(token: string | null) {
  memoryAccessToken = token;
}

export function getAccessTokenInMemory(): string | null {
  return memoryAccessToken;
}

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

/**
 * Custom fetch wrapper that acts as an interceptor.
 * Automatically attaches the in-memory access token as a Bearer header,
 * includes credentials for CORS cookie transmission, and handles 401 refresh retries.
 */
export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getAccessTokenInMemory();
  
  const headers = new Headers(options.headers || {});
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  
  const mergedOptions: RequestInit = {
    ...options,
    headers,
    credentials: "include",
  };

  let response = await fetch(url.startsWith("http") ? url : `${API_BASE_URL}${url}`, mergedOptions);

  if (response.status === 401 && !url.includes("/api/auth/token/refresh/")) {
    if (isRefreshing) {
      return new Promise<Response>(function(resolve, reject) {
        failedQueue.push({ resolve, reject });
      }).then(newToken => {
        const retryHeaders = new Headers(options.headers || {});
        if (newToken) {
          retryHeaders.set("Authorization", `Bearer ${newToken}`);
        }
        return fetch(url.startsWith("http") ? url : `${API_BASE_URL}${url}`, {
          ...options,
          headers: retryHeaders,
          credentials: "include",
        });
      }).catch(err => {
        return Promise.reject(err);
      });
    }

    isRefreshing = true;

    try {
      const refreshRes = await fetch(`${API_BASE_URL}/api/auth/token/refresh/`, {
        method: "POST",
        credentials: "include",
      });
      if (!refreshRes.ok) {
        throw new Error("Refresh failed");
      }
      
      const refreshData = await refreshRes.json();
      setAccessTokenInMemory(refreshData.access);
      
      processQueue(null, refreshData.access);
      
      const retryHeaders = new Headers(options.headers || {});
      retryHeaders.set("Authorization", `Bearer ${refreshData.access}`);
      response = await fetch(url.startsWith("http") ? url : `${API_BASE_URL}${url}`, {
        ...options,
        headers: retryHeaders,
        credentials: "include",
      });
    } catch (err: any) {
      processQueue(err, null);
      setAccessTokenInMemory(null);
      window.location.href = "/login";
    } finally {
      isRefreshing = false;
    }
  }

  return response;
}
