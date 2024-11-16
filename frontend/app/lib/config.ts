export const API_CONFIG = {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    serverUrl: process.env.BACKEND_URL || 'http://backend:8000',
  } as const;
  
  // Helper function for building API URLs
  export const buildApiUrl = (path: string): string => {
    // Use serverUrl for server-side requests (in API routes)
    if (typeof window === 'undefined') {
      return `${API_CONFIG.serverUrl}${path}`;
    }
    // Use baseUrl for client-side requests
    return `${API_CONFIG.baseUrl}${path}`;
  };