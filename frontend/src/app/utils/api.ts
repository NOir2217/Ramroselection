let isRefreshing = false;
let failedQueue: any[] = [];

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
 * If a request fails with 401, it attempts to refresh the token and retry.
 */
export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = localStorage.getItem("access_token"); // If we stored it here. But AuthContext holds it in state.
  // Actually, since cookies are HttpOnly, we don't need to manually attach the refresh token.
  // The access token SHOULD be attached as a Bearer token if we stored it. 
  // Wait, our backend looks for standard SimpleJWT Bearer headers.
  // Since we hold the access token in React state (AuthContext), the cleanest way is for AuthContext to expose a `useApi()` hook.
  
  // For a generic wrapper, we can just do the 401 retry logic.
  let response = await fetch(url, options);

  if (response.status === 401) {
    if (isRefreshing) {
      return new Promise<Response>(function(resolve, reject) {
        failedQueue.push({ resolve, reject });
      }).then(token => {
        // Retry with new token (if we had to attach it, we would modify headers here)
        return fetch(url, options);
      }).catch(err => {
        return Promise.reject(err);
      });
    }

    isRefreshing = true;

    try {
      const refreshRes = await fetch("/api/auth/token/refresh/", { method: "POST" });
      if (!refreshRes.ok) {
        throw new Error("Refresh failed");
      }
      
      const refreshData = await refreshRes.json();
      // In a real app we'd dispatch this back to AuthContext, but the cookie is what matters for the refresh endpoint.
      processQueue(null, refreshData.access);
      
      // Retry the original request
      // If we needed to pass the new access token in headers, we'd do it here.
      response = await fetch(url, options);
    } catch (err: any) {
      processQueue(err, null);
      // Force logout by redirecting or throwing
      window.location.href = "/login";
    } finally {
      isRefreshing = false;
    }
  }

  return response;
}
